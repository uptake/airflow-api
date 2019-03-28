import json
from dateutil.parser import isoparse
from datetime import timezone

from collections import OrderedDict
from flask import Response
from flask_restplus import Resource, fields, Namespace, abort
from airflow.models import DagRun
from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.exceptions import DagRunAlreadyExists
from airflow.utils.timezone import is_localized

from airflowapi.v1.api_blueprint import api
from airflowapi.constants import *
from airflowapi.utilities import airflow_sql_alchemy_session, check_for_dag_id
from airflow.logging_config import log

NAMESPACE_NAME = "dag runs"
NAMESPACE_PATH = "/"

dag_runs = Namespace(
    NAMESPACE_NAME,
    description="Space for interacting with an Airflow DAG's Runs",
    path=NAMESPACE_PATH
)

DAG_ID_KEY = "dag_id"
DAG_RUN_ID_KEY = "dag_run_id"
DAG_RUN_EXECUTION_DATE_KEY = "execution_date"
DAG_RUN_STATE_KEY = "state"
DAG_RUN_START_DATE_KEY = "start_date"
DAG_RUN_END_DATE_KEY = "end_date"

dag_run_model = api.model('Airflow DAG Run', {
    DAG_ID_KEY: fields.String,
    DAG_RUN_ID_KEY: fields.String,
    DAG_RUN_EXECUTION_DATE_KEY: fields.DateTime,
    DAG_RUN_STATE_KEY: fields.String,
    DAG_RUN_START_DATE_KEY: fields.DateTime,
    DAG_RUN_END_DATE_KEY: fields.DateTime
})


DAG_NOT_FOUND_MESSAGE = "DAG not found"
DAG_RUN_NOT_FOUND_MESSAGE = "DAG Run not found"
DAG_RUN_CONFLICT_MESSAGE = "DAG Run already exists"


single_dag_run_body_model = api.model('Airflow Variable Body', OrderedDict([
    (DAG_RUN_EXECUTION_DATE_KEY, fields.DateTime(required=True)),
    (DAG_ID_KEY, fields.String(required=True))
]))

EXECUTION_DATE_BEFORE = "executionDateBefore"
EXECUTION_DATE_AFTER = "executionDateAfter"


def _process_dag_run_to_response_object(dag_run):
    return {
        DAG_ID_KEY: dag_run.dag_id,
        DAG_RUN_ID_KEY: dag_run.run_id,
        DAG_RUN_EXECUTION_DATE_KEY: dag_run.execution_date.isoformat(),
        DAG_RUN_STATE_KEY: dag_run.state,
        DAG_RUN_START_DATE_KEY: dag_run.start_date.isoformat(),
        DAG_RUN_END_DATE_KEY: dag_run.end_date.isoformat() if dag_run.end_date else None
    }


class GetDagRun(Resource):

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, dag_run_model)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def get(self, dag_run_id):
        """Retrieve a DAG Run's Status from Airflow"""
        log.warning("dag_run_id {}".format(dag_run_id))
        with airflow_sql_alchemy_session() as session:
            dr = session.query(DagRun).filter(DagRun.run_id == dag_run_id).first()
        if dr is None:
            abort(NOT_FOUND_RESPONSE_CODE, message=DAG_RUN_NOT_FOUND_MESSAGE)
        response_data = _process_dag_run_to_response_object(dr)
        return Response(
            json.dumps(response_data),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )


class PostDagRun(Resource):
    @api.response(POST_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, dag_run_model)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    @api.response(CONFLICT_RESPONSE_CODE, CONFLICT_DESCRIPTION)
    @api.response(BAD_REQUEST_DESCRIPTION, BAD_REQUEST_DESCRIPTION)
    @api.expect(single_dag_run_body_model, validate=True)
    @api.doc(params={'payload': 'The Request Payload'})
    def post(self):
        """Create a DAG Run from Airflow"""
        try:
            execution_date = isoparse(api.payload[DAG_RUN_EXECUTION_DATE_KEY])
            if not is_localized(execution_date):
                execution_date = execution_date.replace(tzinfo=timezone.utc)
        except ValueError:
            abort(
                BAD_REQUEST_RESPONSE_CODE,
                "Couldn't parse execution date: {execution_date}".format(
                    execution_date=api.payload[DAG_RUN_EXECUTION_DATE_KEY]
                )
            )

        dag_id = api.payload[DAG_ID_KEY]
        if check_for_dag_id(dag_id) is None:
            abort(NOT_FOUND_RESPONSE_CODE, message=DAG_NOT_FOUND_MESSAGE)
        try:
            dr = trigger_dag(
                dag_id=dag_id,
                execution_date=execution_date
            )
            response_data = _process_dag_run_to_response_object(dr)
            return Response(
                json.dumps(response_data),
                status=POST_RESPONSE_SUCCESS_CODE,
                mimetype=JSON_MIME_TYPE
            )
        except DagRunAlreadyExists:
            abort(CONFLICT_RESPONSE_CODE, DAG_RUN_CONFLICT_MESSAGE)


dag_runs.add_resource(PostDagRun, '')
dag_runs.add_resource(GetDagRun, '/<string:dag_run_id>')

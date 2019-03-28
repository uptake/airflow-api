import json
import os

from airflowapi.v1.dag_runs import EXECUTION_DATE_BEFORE, EXECUTION_DATE_AFTER

from airflowapi.v1.url_parameter import APIParam
from flask import Response
from flask_restplus import Resource, fields, Namespace, abort, inputs
from flask_restplus.reqparse import RequestParser
from airflow.models import DagModel, DagBag, DagRun
from airflow.bin.cli import process_subdir
from airflow.exceptions import AirflowException

from airflowapi.v1.api_blueprint import api
from airflowapi.constants import *
from airflowapi.utilities import airflow_sql_alchemy_session, check_for_dag_id
from airflowapi.v1.dag_runs import dag_run_model, _process_dag_run_to_response_object

from airflow.logging_config import log


class DagArgs:
    def __init__(self, subdir, dag_id=None):
        self.subdir = subdir
        self.dag_id = dag_id


NAMESPACE_NAME = "dags"
NAMESPACE_PATH = "/"

PAUSE_ROUTE = "/pause"
UNPAUSE_ROUTE = "/unpause"
DAG_RUNS_ROUTE = "/dag-runs"

DAG_ID_KEY = "dag_id"
IS_PAUSED_KEY = "is_paused"
FILE_LOCATION_KEY = "file_location"
NOT_FOUND_MESSAGE = "DAG not found"

SUBDIR_VALUE = "DAGS_FOLDER"
ALLOWED_EXTENSIONS = ["py"]

dag_model = api.model('Airflow DAG', {
    DAG_ID_KEY: fields.String,
    IS_PAUSED_KEY: fields.Boolean,
    FILE_LOCATION_KEY: fields.String
})

dags = Namespace(
    NAMESPACE_NAME,
    description="Space for interacting with Airflow DAG's",
    path=NAMESPACE_PATH
)

execution_date_before = APIParam(
    name=EXECUTION_DATE_BEFORE,
    data_type=inputs.datetime_from_iso8601,
    required=False,
    default=None,
    param_help="A field to specify a datetime that will be used to filter the DAG runs returned based on their execution date being prior to the datetime"
)

execution_date_after = APIParam(
    name=EXECUTION_DATE_AFTER,
    data_type=inputs.datetime_from_iso8601,
    required=False,
    default=None,
    param_help="A field to specify a datetime that will be used to filter the DAG runs returned based on their execution date being after to the datetime"
)


def _process_dag_to_response(dag):
    return {DAG_ID_KEY: dag.dag_id, IS_PAUSED_KEY: dag.is_paused, FILE_LOCATION_KEY: dag.fileloc}


class SingleDag(Resource):

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, dag_model)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def get(self, dag_id):
        """Retrieve a DAG's Status from Airflow"""
        dag = check_for_dag_id(dag_id)
        if dag is None:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        return Response(
            response=json.dumps(_process_dag_to_response(dag)),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )

    @api.response(DELETE_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def delete(self, dag_id):
        """Delete a DAG from Airflow (This will delete the file containing the DAG)"""
        dag = check_for_dag_id(dag_id)
        if dag is None:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        with airflow_sql_alchemy_session() as session:
            try:
                os.unlink(dag.fileloc)
            except FileNotFoundError:
                pass
            session.query(DagModel).filter(DagModel.dag_id == dag.dag_id).delete()
            session.commit()
        return Response(status=DELETE_RESPONSE_SUCCESS_CODE)


class MultiDag(Resource):

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, [dag_model])
    def get(self):
        """Get all DAGs' statuses in Airflow"""
        dag_bag = DagBag(process_subdir(SUBDIR_VALUE))
        log.warning(SUBDIR_VALUE)
        log.warning(dag_bag)
        response_data = [_process_dag_to_response(dag) for dag in dag_bag.dags.values()]
        return Response(
            json.dumps(response_data),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )


def set_is_paused(is_paused, dag_id):
    with airflow_sql_alchemy_session() as session:
        dm = session.query(DagModel).filter(
            DagModel.dag_id == dag_id
        ).first()
        dm.is_paused = is_paused
        session.commit()


class PauseDag(Resource):
    @api.response(PUT_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def put(self, dag_id):
        """Pause a DAG in Airflow"""
        try:
            if not check_for_dag_id(dag_id):
                abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        except AirflowException:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        set_is_paused(True, dag_id)
        return Response(status=PUT_RESPONSE_SUCCESS_CODE)


class UnpauseDag(Resource):
    @api.response(PUT_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, dag_model)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def put(self, dag_id):
        """Unpause a DAG in Airflow"""
        try:
            if not check_for_dag_id(dag_id):
                abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        except AirflowException:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        set_is_paused(False, dag_id)
        return Response(status=PUT_RESPONSE_SUCCESS_CODE)


class DagRuns(Resource):
    get_parser = RequestParser(bundle_errors=True)
    get_parser.add_argument(
        execution_date_before.name,
        type=execution_date_before.data_type,
        required=execution_date_before.required,
        help=execution_date_before.param_help
    )
    get_parser.add_argument(
        execution_date_after.name,
        type=execution_date_after.data_type,
        required=execution_date_after.required,
        help=execution_date_after.param_help
    )

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, [dag_run_model])
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    @api.expect(get_parser, validate=True)
    def get(self, dag_id):
        """Get all DAG Run's for a DAG in Airflow"""
        args = self.get_parser.parse_args()
        log.warning("dag_id {}".format(dag_id))
        log.warning("before {}".format(args.get(execution_date_before.name)))
        log.warning("after {}".format(args.get(execution_date_after.name)))
        if check_for_dag_id(dag_id) is None:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
        with airflow_sql_alchemy_session() as session:
            query = session.query(DagRun).filter(DagRun.dag_id == dag_id)
            if args.get(execution_date_before.name):
                query = query.filter(DagRun.execution_date < args.get(execution_date_before.name))
            if args.get(execution_date_after.name):
                query = query.filter(DagRun.execution_date > args.get(execution_date_after.name))
            drs = query.all()
        response_data = [_process_dag_run_to_response_object(dag_run) for dag_run in drs]
        return Response(
            json.dumps(response_data),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )


dags.add_resource(SingleDag, '/<string:dag_id>')
dags.add_resource(DagRuns, '/<string:dag_id>{dag_runs_route}'.format(dag_runs_route=DAG_RUNS_ROUTE))
dags.add_resource(MultiDag, '')
dags.add_resource(UnpauseDag, '/<string:dag_id>{unpause_route}'.format(unpause_route=UNPAUSE_ROUTE))
dags.add_resource(PauseDag, '/<string:dag_id>{pause_route}'.format(pause_route=PAUSE_ROUTE))

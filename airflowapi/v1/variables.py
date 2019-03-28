import json
from collections import OrderedDict

from flask import Response
from flask_restplus import Resource, fields, inputs, Namespace, abort
from flask_restplus.reqparse import RequestParser
from airflow.models import Variable

from airflowapi.v1.api_blueprint import api
from airflowapi.constants import *
from airflowapi.v1.url_parameter import APIParam
from airflowapi.utilities import airflow_sql_alchemy_session


NAMESPACE_NAME = "variables"
NAMESPACE_PATH = "/"

NAME_KEY = "name"
VALUE_KEY = "value"
DESERIALIZE_JSON_KEY = "deserialize_json"
NOT_FOUND_MESSAGE = "Variable not found"

variables = Namespace(
    NAMESPACE_NAME,
    description='Space for interacting with Airflow Variables',
    path=NAMESPACE_PATH
)

airflow_variable_model = api.model('Airflow Variable', {
    NAME_KEY: fields.String,
    VALUE_KEY: fields.String,
    DESERIALIZE_JSON_KEY: fields.Boolean
})

single_airflow_variable_body_model = api.model('Airflow Variable Body', OrderedDict([
    (VALUE_KEY, fields.String(required=True)),
    (DESERIALIZE_JSON_KEY, fields.Boolean(required=True, default=False)),
]))

multi_airflow_variable_body_model = api.model('Airflow Multiple Variable Body', OrderedDict([
    (NAME_KEY, fields.String(required=True)),
    (VALUE_KEY, fields.String(required=True)),
    (DESERIALIZE_JSON_KEY, fields.Boolean(required=True, default=False)),
]))

deserialize_json_param = APIParam(
    name=DESERIALIZE_JSON_KEY,
    data_type=inputs.boolean,
    required=False,
    default=False,
    param_help="A field to indicate that the value in the Variable value should be treated as JSON. Default to false"
)


def set_airflow_variable(var_name, raw_var_value, deserialize_json, session):
    var_value = json.loads(raw_var_value) if deserialize_json else raw_var_value
    Variable.set(
        key=var_name,
        value=var_value,
        serialize_json=deserialize_json,
        session=session
    )
    return Variable.get(var_name, deserialize_json=deserialize_json)


class SingleVariable(Resource):
    get_parser = RequestParser(bundle_errors=True)
    get_parser.add_argument(
        deserialize_json_param.name,
        type=deserialize_json_param.data_type,
        required=deserialize_json_param.required,
        default=deserialize_json_param.default,
        help=deserialize_json_param.param_help
    )

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, airflow_variable_model)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    @api.expect(get_parser, validate=True)
    def get(self, var_name):
        """Retrieve a single variable value from Airflow"""
        args = self.get_parser.parse_args()
        try:
            deserialize_json = args.get(deserialize_json_param.name)
            var = Variable.get(var_name, deserialize_json=deserialize_json)
        except KeyError:
            abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)

        response = {
            NAME_KEY: var_name,
            VALUE_KEY: var,
            DESERIALIZE_JSON_KEY: deserialize_json
        }
        return Response(
            response=json.dumps(response),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )

    @api.response(POST_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, airflow_variable_model)
    @api.expect(single_airflow_variable_body_model, validate=True)
    @api.doc(params={'payload': 'The Request Payload'})
    def post(self, var_name):
        """Create/Update a single variable in Airflow"""
        with airflow_sql_alchemy_session() as session:
            deserialize_json = api.payload[deserialize_json_param.name]
            raw_var_value = api.payload[VALUE_KEY]
            var = set_airflow_variable(var_name, raw_var_value, deserialize_json, session)
            session.commit()
        response = {
            NAME_KEY: var_name,
            VALUE_KEY: var,
            DESERIALIZE_JSON_KEY: deserialize_json
        }
        return Response(
            response=json.dumps(response),
            status=POST_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )

    @api.response(DELETE_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    def delete(self, var_name):
        """Delete a single variable in Airflow"""
        with airflow_sql_alchemy_session() as session:
            query = session.query(Variable).filter_by(key=var_name)
            if len(query.all()) == 0:
                abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)
            session.query(Variable).filter_by(key=var_name).delete()
            session.commit()
        return Response(status=DELETE_RESPONSE_SUCCESS_CODE)


class MultiVariable(Resource):

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, [airflow_variable_model])
    def get(self):
        """Get all variables in Airflow"""
        with airflow_sql_alchemy_session() as session:
            airflow_variables = session.query(Variable).all()
        var_list = []
        d = json.JSONDecoder()
        for var in airflow_variables:
            val = None
            deserialize_json = True
            try:
                val = d.decode(var.val)
            except Exception:
                val = var.val
                deserialize_json = False
            var_list.append({
                NAME_KEY: var.key,
                VALUE_KEY: val,
                DESERIALIZE_JSON_KEY: deserialize_json
            })
        return Response(
            response=json.dumps(var_list),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )

    @api.response(POST_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, [airflow_variable_model])
    @api.response(POST_RESPONSE_SUCCESS_CODE, BAD_REQUEST_DESCRIPTION)
    @api.expect([multi_airflow_variable_body_model], validate=True)
    @api.doc(params={'payload': 'The Request Payload'})
    def post(self):
        """Create/Update multiple variables in Airflow"""
        if len(api.payload) == 0:
            abort(BAD_REQUEST_RESPONSE_CODE, messsage="No Variables were supplied to Create/Update")
        variables_created = []
        with airflow_sql_alchemy_session() as session:
            for var in api.payload:
                var_name = var[NAME_KEY]
                deserialize_json = var[deserialize_json_param.name]
                var_value = set_airflow_variable(var_name, var[VALUE_KEY], deserialize_json, session)
                variables_created.append({
                    NAME_KEY: var_name,
                    VALUE_KEY: var_value,
                    DESERIALIZE_JSON_KEY: deserialize_json
                })
            session.commit()
        return Response(
            response=json.dumps(variables_created),
            status=POST_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )


variables.add_resource(SingleVariable, '/<string:var_name>')
variables.add_resource(MultiVariable, '')

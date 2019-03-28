import os
import json

from flask import Response
from flask_restplus import Namespace, Resource, fields, abort
from flask_restplus.reqparse import RequestParser
from werkzeug.datastructures import FileStorage
from airflow import settings

from airflowapi.v1.api_blueprint import api
from airflowapi.constants import *
from airflowapi.v1.url_parameter import APIParam

NAMESPACE_NAME = "files"
NAMESPACE_PATH = ""

FILE_KEY = "file"
ALLOWED_EXTENSIONS = ["py"]
NOT_FOUND_MESSAGE = "File not found in airflow server"

dag_files = Namespace(
    NAMESPACE_NAME,
    description="Space for interacting with Airflow DAG Files",
    path=NAMESPACE_PATH
)

dag_file_model = api.model('Airflow DAG File', {
    FILE_KEY: fields.String
})

file_parameter = APIParam(
    name=FILE_KEY,
    data_type=str,
    required=True,
    param_help="The filename to act upon in the Airflow DAG Files"
)


def check_for_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    if not check_for_allowed_file(filename):
        abort(
            BAD_REQUEST_RESPONSE_CODE,
            message="File has an improper extension. Allowed Extensions are {allowed_extensions}".format(
                allowed_extensions=ALLOWED_EXTENSIONS
            )
        )


def check_for_file(dag_file_path):
    if not os.path.isfile(dag_file_path):
        abort(NOT_FOUND_RESPONSE_CODE, message=NOT_FOUND_MESSAGE)


def validate_file_for_upload(file):
    if file.filename == '':
        abort(BAD_REQUEST_RESPONSE_CODE, message="File Was Not Provided")
    allowed_file(file.filename)


class DagFiles(Resource):

    @api.response(GET_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION, [dag_file_model])
    def get(self):
        """Get DAG Files present on Airflow"""
        files = [{FILE_KEY: file} for file in os.listdir(settings.DAGS_FOLDER) if check_for_allowed_file(file)]
        return Response(
            json.dumps(files),
            status=GET_RESPONSE_SUCCESS_CODE,
            mimetype=JSON_MIME_TYPE
        )

    post_parser = RequestParser(bundle_errors=True)
    post_parser.add_argument(FILE_KEY, location='files', type=FileStorage, required=True)

    @api.response(POST_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(BAD_REQUEST_RESPONSE_CODE, BAD_REQUEST_DESCRIPTION)
    @api.response(CONFLICT_RESPONSE_CODE, CONFLICT_DESCRIPTION)
    @api.expect(post_parser, validate=True)
    def post(self):
        """Upload a DAG File to Airflow"""
        args = self.post_parser.parse_args()
        file = args.get(FILE_KEY)
        dag_file_path = os.path.join(settings.DAGS_FOLDER, file.filename)

        validate_file_for_upload(file)
        if os.path.isfile(dag_file_path):
            abort(CONFLICT_RESPONSE_CODE, message="File Already Exists")

        file.save(dag_file_path)
        return Response(status=POST_RESPONSE_SUCCESS_CODE)

    @api.response(PUT_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(BAD_REQUEST_RESPONSE_CODE, BAD_REQUEST_DESCRIPTION)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    @api.expect(post_parser, validate=True)
    def put(self):
        """Update an existing DAG File to Airflow"""
        args = self.post_parser.parse_args()
        file = args.get(FILE_KEY)
        dag_file_path = os.path.join(settings.DAGS_FOLDER, file.filename)

        validate_file_for_upload(file)
        check_for_file(dag_file_path)

        file.save(dag_file_path)
        return Response(status=PUT_RESPONSE_SUCCESS_CODE)

    delete_parser = RequestParser(bundle_errors=True)
    delete_parser.add_argument(
        file_parameter.name,
        type=file_parameter.data_type,
        required=file_parameter.required,
        help=file_parameter.param_help
    )

    @api.response(DELETE_RESPONSE_SUCCESS_CODE, SUCCESS_DESCRIPTION)
    @api.response(BAD_REQUEST_RESPONSE_CODE, BAD_REQUEST_DESCRIPTION)
    @api.response(NOT_FOUND_RESPONSE_CODE, NOT_FOUND_DESCRIPTION)
    @api.expect(delete_parser, validate=True)
    def delete(self):
        """Delete a DAG File from Airflow"""
        args = self.delete_parser.parse_args()
        filename = args.get(FILE_KEY)
        filepath = os.path.join(settings.DAGS_FOLDER, filename)

        allowed_file(filename)
        check_for_file(filepath)

        os.unlink(filepath)
        return Response(status=DELETE_RESPONSE_SUCCESS_CODE)


dag_files.add_resource(DagFiles, '')

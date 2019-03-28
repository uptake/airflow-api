from flask_restplus import Resource, fields
from airflowapi.v1.api_blueprint import api
from airflowapi.version import version

health = api.model('Health', {
    'version': fields.String,
    'health': fields.String
})


class Health(Resource):

    @api.response(200, "Success", health)
    def get(self):
        """Retrieve version and health of API"""
        response = {
            "version": version,
            "health": "ok"
        }
        return response

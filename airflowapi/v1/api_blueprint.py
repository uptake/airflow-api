
from flask import Blueprint
from airflowapi.version import version
from flask_restplus import Api
from airflow.www.app import csrf

URL_PREFIX = "/api/v1"
BLUEPRINT_NAME = "v1"
DOCUMENTATION_ROUTE = "/doc"
HEALTH_ROUTE = "/health"
VARIABLES_RESOURCE_ROUTE = '/variables'
DAGS_RESOURCE_ROUTE = "/dags"
DAG_RUNS_RESOURCE_ROUTE = "/dag-runs"
DAG_FILES_RESOURCE_ROUTE = "/files"

blueprint = Blueprint(BLUEPRINT_NAME, __name__, url_prefix=URL_PREFIX)
csrf.exempt(blueprint)


@blueprint.record
def record_params(setup_state):
    app = setup_state.app
    app.config["ERROR_404_HELP"] = False


api = Api(
    blueprint,
    title='Airflow API',
    version=version,
    description='API for Pulling Data From Airflow',
    doc=DOCUMENTATION_ROUTE
)

from airflowapi.v1.health import Health
from airflowapi.v1.variables import variables
from airflowapi.v1.dags import dags
from airflowapi.v1.dag_files import dag_files
from airflowapi.v1.dag_runs import dag_runs

api.add_resource(Health, HEALTH_ROUTE)
api.add_namespace(variables, VARIABLES_RESOURCE_ROUTE)
api.add_namespace(dags, DAGS_RESOURCE_ROUTE)
api.add_namespace(dag_files, DAG_FILES_RESOURCE_ROUTE)
api.add_namespace(dag_runs, DAG_RUNS_RESOURCE_ROUTE)

from airflow.plugins_manager import AirflowPlugin
from airflowapi.v1.api_blueprint import blueprint


class AirflowAPIPlugin(AirflowPlugin):
    name = "airflow_api"
    flask_blueprints = [blueprint]

import pytest
import requests
from time import sleep
from datetime import datetime, timezone, timedelta
import json

from airflowapi.constants import \
    GET_RESPONSE_SUCCESS_CODE, \
    POST_RESPONSE_SUCCESS_CODE, \
    DELETE_RESPONSE_SUCCESS_CODE, \
    NOT_FOUND_RESPONSE_CODE
from airflowapi.v1.api_blueprint import URL_PREFIX, VARIABLES_RESOURCE_ROUTE, DAG_FILES_RESOURCE_ROUTE,\
    DAGS_RESOURCE_ROUTE, DAG_RUNS_RESOURCE_ROUTE
from airflowapi.v1.dag_runs import DAG_ID_KEY, DAG_RUN_EXECUTION_DATE_KEY, DAG_RUN_END_DATE_KEY, DAG_RUN_STATE_KEY


DOCKER_API_SERVICE_NAME = "airflow-webserver"
DOCKER_API_PORT = "8080"
DAG_REQUEST_TIMEOUT = 30

DAY_OFFSET = 10

class TestDagFile:
    def __init__(self, filename, dag_id, dag):
        self.filename = filename
        self.dag_id = dag_id
        self.post_data = {'file': (filename, dag)}


def check_for_dag(uri):
    get_resp = requests.get(uri)
    if get_resp.status_code == GET_RESPONSE_SUCCESS_CODE:
        return True
    elif get_resp.status_code == NOT_FOUND_RESPONSE_CODE:
        return False
    else:
        get_resp.raise_for_status()


@pytest.fixture(scope='session')
def test_dag_id(request):
    return "my_dag"


@pytest.fixture(scope='session')
def test_dag_filename(request, test_dag_id):
    return "{test_dag_id}.py".format(test_dag_id=test_dag_id)


@pytest.fixture(scope='session')
def test_dag_string(request, test_dag_id):
    dag = """
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta


default_args = {
    'owner': 'my-test-user',
    'depends_on_past': False,
    'start_date': datetime(2018,10,1),
    'retries': 1,
    'retry_delay': timedelta(minutes=15)
}

dag = DAG(
    "{{dag_id}}",
    default_args=default_args,
    schedule_interval='0 0 * * *'
)
task_1 = DummyOperator(dag=dag, task_id="task1")
task_2 = DummyOperator(dag=dag, task_id="task2")
task_1.set_downstream(task_2)
""".replace("{{dag_id}}", test_dag_id)
    return dag


@pytest.fixture(scope='session')
def json_header(request):
    return {"Content-Type": "application/json"}


@pytest.fixture(scope='session')
def test_dag_file_data(request, test_dag_filename, test_dag_string):
    files = {'file': (test_dag_filename, test_dag_string)}
    return files


@pytest.fixture(scope='session')
def test_dag_file(request, test_dag_filename, test_dag_id, test_dag_string):
    return TestDagFile(test_dag_filename, test_dag_id, test_dag_string)


@pytest.fixture(scope='session')
def api_uri(request):
    return "http://{host}:{port}{prefix}".format(host=DOCKER_API_SERVICE_NAME, port=DOCKER_API_PORT, prefix=URL_PREFIX)


@pytest.fixture(scope='session')
def dag_files_resource_uri(request, api_uri):
    return "{api_uri}{route}".format(api_uri=api_uri, route=DAG_FILES_RESOURCE_ROUTE)


@pytest.fixture(scope='session')
def dags_resource_uri(request, api_uri):
    return "{api_uri}{route}".format(api_uri=api_uri, route=DAGS_RESOURCE_ROUTE)


@pytest.fixture(scope='session')
def dag_by_dag_id_format(request, dags_resource_uri):
    return "{base_uri}/{{dag_id}}".format(base_uri=dags_resource_uri)


@pytest.fixture(scope='session')
def variables_resource_uri(request, api_uri):
    return "{api_uri}{route}".format(api_uri=api_uri, route=VARIABLES_RESOURCE_ROUTE)


@pytest.fixture(scope='session')
def dag_runs_resource_uri(request, api_uri):
    return "{api_uri}{route}".format(api_uri=api_uri, route=DAG_RUNS_RESOURCE_ROUTE)


@pytest.fixture
def test_dag_file_on_server(request, dag_by_dag_id_format, test_dag_file, dag_files_resource_uri):
    post_resp = requests.post(dag_files_resource_uri, files=test_dag_file.post_data)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
    dag_url = dag_by_dag_id_format.format(dag_id=test_dag_file.dag_id)

    def tear_down_file():
        delete_resp = requests.delete(dag_files_resource_uri, params={"file": test_dag_file.filename})
        assert delete_resp.status_code in [DELETE_RESPONSE_SUCCESS_CODE, NOT_FOUND_RESPONSE_CODE]
        delete_resp = requests.delete(dag_url)
        assert delete_resp.status_code in [DELETE_RESPONSE_SUCCESS_CODE, NOT_FOUND_RESPONSE_CODE]
    try:
        started_at = datetime.now()
        while not check_for_dag(dag_url):
            if (datetime.now() - started_at).total_seconds() > DAG_REQUEST_TIMEOUT:
                raise RuntimeError("Timeout Occurred Waiting for DAG")
            sleep(1)
        request.addfinalizer(tear_down_file)
    except Exception as e:
        tear_down_file()
        raise e
    return test_dag_file


@pytest.fixture
def test_execution_date(request):
    return datetime.utcnow().replace(microsecond=0).replace(tzinfo=timezone.utc)


@pytest.fixture
def dag_run_payload(request, test_dag_id, test_execution_date):
    return {
        DAG_ID_KEY: test_dag_id,
        DAG_RUN_EXECUTION_DATE_KEY: test_execution_date.isoformat()
    }


@pytest.fixture
def future_dag_run_payload(request, test_dag_id, test_execution_date):
    return {
        DAG_ID_KEY: test_dag_id,
        DAG_RUN_EXECUTION_DATE_KEY: (test_execution_date + timedelta(days=DAY_OFFSET)).isoformat()
    }


@pytest.fixture
def past_dag_run_payload(request, test_dag_id, test_execution_date):
    return {
        DAG_ID_KEY: test_dag_id,
        DAG_RUN_EXECUTION_DATE_KEY: (test_execution_date + timedelta(days=(-1 * DAY_OFFSET))).isoformat()
    }


@pytest.fixture(scope='session')
def changing_dag_run_keys(request):
    return [DAG_RUN_END_DATE_KEY, DAG_RUN_STATE_KEY]


@pytest.fixture
def existing_dag_run(request, test_dag_file_on_server, dag_runs_resource_uri, dag_run_payload, json_header):
    post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(dag_run_payload), headers=json_header)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
    return post_resp.json()


@pytest.fixture
def existing_dag_run_in_future(
        request,
        test_dag_file_on_server,
        dag_runs_resource_uri,
        future_dag_run_payload,
        json_header
):
    post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(future_dag_run_payload), headers=json_header)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
    return post_resp.json()

@pytest.fixture
def existing_dag_run_in_past(
        request,
        test_dag_file_on_server,
        dag_runs_resource_uri,
        past_dag_run_payload,
        json_header
):
    post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(past_dag_run_payload), headers=json_header)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
    return post_resp.json()

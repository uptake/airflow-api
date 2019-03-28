import requests
import os
from time import sleep
from datetime import timedelta
from dateutil.parser import isoparse

from airflowapi.constants import \
    GET_RESPONSE_SUCCESS_CODE, \
    DELETE_RESPONSE_SUCCESS_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    PUT_RESPONSE_SUCCESS_CODE
from airflowapi.v1.dags import FILE_LOCATION_KEY, DAG_ID_KEY, IS_PAUSED_KEY, PAUSE_ROUTE, UNPAUSE_ROUTE
from airflowapi.v1.dag_runs import DAG_RUN_EXECUTION_DATE_KEY, EXECUTION_DATE_BEFORE, EXECUTION_DATE_AFTER, \
    DAG_RUN_ID_KEY
from airflowapi.v1.api_blueprint import DAG_RUNS_RESOURCE_ROUTE

DAG_RUNS_BY_DAG_ID_FORMAT = "{{base_uri}}{dag_run_route}".format(dag_run_route=DAG_RUNS_RESOURCE_ROUTE)

class TestGetDagsResource:
    def test_get_dags_works_with_dag(self, dags_resource_uri, test_dag_file_on_server):
        get_resp = requests.get(dags_resource_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert len(body) == 1
        assert os.path.basename(body[0][FILE_LOCATION_KEY]) == test_dag_file_on_server.filename
        assert body[0][DAG_ID_KEY] == test_dag_file_on_server.dag_id

    def test_get_dags_works_without_dag(self, dags_resource_uri):
        get_resp = requests.get(dags_resource_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        assert len(get_resp.json()) == 0


class TestGetDagByIdResource:
    def test_get_dag_by_id_works(self, test_dag_file_on_server, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id=test_dag_file_on_server.dag_id)
        get_resp = requests.get(uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert os.path.basename(body[FILE_LOCATION_KEY]) == test_dag_file_on_server.filename
        assert body[DAG_ID_KEY] == test_dag_file_on_server.dag_id

    def test_get_dag_by_id_will_throw_404(self, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id="123")
        get_resp = requests.get(uri)
        assert get_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestDeleteDagByIdResource:
    def test_delete_dag_by_id_works(self, test_dag_file_on_server, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id=test_dag_file_on_server.dag_id)
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

    def test_delete_by_dag_id_will_throw_404(self, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id="123")
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestPauseDagByDagIdResource:
    def test_pause_dag_by_id_works(self, test_dag_file_on_server, dag_by_dag_id_format):
        sleep(10)
        base_uri = dag_by_dag_id_format.format(dag_id=test_dag_file_on_server.dag_id)
        pause_uri = base_uri + PAUSE_ROUTE
        put_resp = requests.put(pause_uri)
        assert put_resp.status_code == PUT_RESPONSE_SUCCESS_CODE
        get_resp = requests.get(base_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        assert get_resp.json()[IS_PAUSED_KEY]

    def test_pause_dag_by_id_will_throw_404(self, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id="123") + PAUSE_ROUTE
        put_resp = requests.put(uri)
        assert put_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestUnpauseDagByDagIdResource:
    def test_pause_dag_by_id_works(self, dag_by_dag_id_format, test_dag_file_on_server):
        base_uri = dag_by_dag_id_format.format(dag_id=test_dag_file_on_server.dag_id)
        pause_uri = base_uri + UNPAUSE_ROUTE
        put_resp = requests.put(pause_uri)
        assert put_resp.status_code == PUT_RESPONSE_SUCCESS_CODE
        get_resp = requests.get(base_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        assert not get_resp.json()[IS_PAUSED_KEY]

    def test_pause_dag_by_id_will_throw_404(self, dag_by_dag_id_format):
        uri = dag_by_dag_id_format.format(dag_id="123") + UNPAUSE_ROUTE
        put_resp = requests.put(uri)
        assert put_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestGetDagRunsByDagIdResource:
    def test_get_dag_runs_by_dag_id_works(self, dag_by_dag_id_format, existing_dag_run, changing_dag_run_keys):
        base_uri = dag_by_dag_id_format.format(dag_id=existing_dag_run[DAG_ID_KEY])
        url = DAG_RUNS_BY_DAG_ID_FORMAT.format(base_uri=base_uri)
        get_resp = requests.get(url)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        get_body = get_resp.json()
        dag_runs = [run for run in get_body if run[DAG_RUN_ID_KEY] == existing_dag_run[DAG_RUN_ID_KEY]]
        assert len(dag_runs) == 1
        dr = dag_runs[0]
        for key, item in existing_dag_run.items():
            if key not in changing_dag_run_keys:
                assert dr[key] == item
            else:
                assert key in dr

    def test_get_dag_runs_by_dag_id_before_filter_works(
            self,
            dag_by_dag_id_format,
            existing_dag_run_in_future,
            changing_dag_run_keys
    ):
        base_uri = dag_by_dag_id_format.format(dag_id=existing_dag_run_in_future[DAG_ID_KEY])
        url = DAG_RUNS_BY_DAG_ID_FORMAT.format(base_uri=base_uri)
        before_date = isoparse(existing_dag_run_in_future[DAG_RUN_EXECUTION_DATE_KEY]) + timedelta(days=1)
        get_resp = requests.get(url, params={EXECUTION_DATE_BEFORE: before_date.isoformat()})
        assert(get_resp.status_code == GET_RESPONSE_SUCCESS_CODE)
        resp_body = get_resp.json()
        dag_runs = [run for run in resp_body if run[DAG_RUN_ID_KEY] == existing_dag_run_in_future[DAG_RUN_ID_KEY]]
        assert len(dag_runs) == 1
        dr = dag_runs[0]
        for key, item in existing_dag_run_in_future.items():
            if key not in changing_dag_run_keys:
                assert dr[key] == item
            else:
                assert key in dr

    def test_get_dag_runs_by_dag_id_after_filter_works(
            self,
            dag_by_dag_id_format,
            existing_dag_run_in_past,
            changing_dag_run_keys
    ):
        base_uri = dag_by_dag_id_format.format(dag_id=existing_dag_run_in_past[DAG_ID_KEY])
        url = DAG_RUNS_BY_DAG_ID_FORMAT.format(base_uri=base_uri)
        after_date = isoparse(existing_dag_run_in_past[DAG_RUN_EXECUTION_DATE_KEY]) + timedelta(days=-1)
        get_resp = requests.get(url, params={EXECUTION_DATE_AFTER: after_date.isoformat()})
        assert(get_resp.status_code == GET_RESPONSE_SUCCESS_CODE)
        resp_body = get_resp.json()
        dag_runs = [run for run in resp_body if run[DAG_RUN_ID_KEY] == existing_dag_run_in_past[DAG_RUN_ID_KEY]]
        assert len(dag_runs) == 1
        dr = dag_runs[0]
        for key, item in existing_dag_run_in_past.items():
            if key not in changing_dag_run_keys:
                assert dr[key] == item
            else:
                assert key in dr


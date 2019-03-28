import pytest
import requests
import json

from airflow.utils.state import State
from dateutil.parser import isoparse

from airflowapi.constants import \
    GET_RESPONSE_SUCCESS_CODE, \
    POST_RESPONSE_SUCCESS_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    CONFLICT_RESPONSE_CODE, \
    BAD_REQUEST_RESPONSE_CODE
from airflowapi.v1.dag_runs import DAG_ID_KEY, DAG_RUN_EXECUTION_DATE_KEY, DAG_RUN_START_DATE_KEY,\
    DAG_RUN_END_DATE_KEY, DAG_RUN_ID_KEY, DAG_RUN_STATE_KEY

GET_DAG_RUN_BY_ID_ROUTE = "{url}/{dag_run_id}"


class TestPostDagRunResource:
    def test_post_dag_run_works_with_dag_id(
            self,
            dag_runs_resource_uri,
            dag_run_payload,
            test_dag_file_on_server,
            test_execution_date,
            json_header
    ):
        post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(dag_run_payload), headers=json_header)
        assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
        resp_body = post_resp.json()
        assert test_dag_file_on_server.dag_id == resp_body[DAG_ID_KEY]
        assert test_execution_date == isoparse(resp_body[DAG_RUN_EXECUTION_DATE_KEY])
        assert resp_body[DAG_RUN_START_DATE_KEY] is not None
        assert resp_body[DAG_RUN_END_DATE_KEY] is None
        assert resp_body[DAG_RUN_ID_KEY] is not None
        assert resp_body[DAG_RUN_STATE_KEY] in State.dag_states

    def test_post_dag_run_will_not_post_empty_data(self, dag_runs_resource_uri, json_header):
        post_resp = requests.post(dag_runs_resource_uri, data=json.dumps([]), headers=json_header)
        assert post_resp.status_code == BAD_REQUEST_RESPONSE_CODE

    def test_post_dag_run_will_throw_a_409(
            self,
            dag_runs_resource_uri,
            dag_run_payload,
            test_dag_file_on_server,
            json_header
    ):
        post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(dag_run_payload), headers=json_header)
        assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
        post_resp = requests.post(dag_runs_resource_uri, data=json.dumps(dag_run_payload), headers=json_header)
        assert post_resp.status_code == CONFLICT_RESPONSE_CODE

    def test_post_dag_run_will_throw_a_404(
            self,
            dag_runs_resource_uri,
            test_execution_date,
            json_header
    ):
        post_resp = requests.post(
            dag_runs_resource_uri,
            data=json.dumps(
                {
                    DAG_RUN_EXECUTION_DATE_KEY: test_execution_date.isoformat(),
                    DAG_ID_KEY: "THISISINVALID"
                }
            ),
            headers=json_header
        )
        assert post_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestGetDagRunsResource:

    def test_get_dag_run_by_id_works(self, dag_runs_resource_uri, existing_dag_run, changing_dag_run_keys):
        get_url = GET_DAG_RUN_BY_ID_ROUTE.format(url=dag_runs_resource_uri, dag_run_id=existing_dag_run[DAG_RUN_ID_KEY])
        get_resp = requests.get(get_url)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        get_body = get_resp.json()
        for key, item in existing_dag_run.items():
            if key not in changing_dag_run_keys:
                assert get_body[key] == item
        for key in changing_dag_run_keys:
            assert key in get_body

    def test_get_dag_run_by_id_throws_404(self, dag_runs_resource_uri):
        get_url = GET_DAG_RUN_BY_ID_ROUTE.format(url=dag_runs_resource_uri, dag_run_id="THISISINVALID")
        get_resp = requests.get(get_url)
        assert get_resp.status_code == NOT_FOUND_RESPONSE_CODE

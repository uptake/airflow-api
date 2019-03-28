import pytest
import requests
import json

from airflowapi.constants import \
    GET_RESPONSE_SUCCESS_CODE, \
    DELETE_RESPONSE_SUCCESS_CODE, \
    POST_RESPONSE_SUCCESS_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    BAD_REQUEST_RESPONSE_CODE

from airflowapi.v1.variables import NAME_KEY, VALUE_KEY, DESERIALIZE_JSON_KEY


@pytest.fixture(scope='module')
def json_key(request):
    return "my_key"


@pytest.fixture(scope='module')
def json_value(request):
    return 1


@pytest.fixture(scope='module')
def variable_payload(request):
    return {
        NAME_KEY: "TEST_VAR",
        VALUE_KEY: "TEST_VALUE",
        DESERIALIZE_JSON_KEY: False
    }


@pytest.fixture(scope='module')
def json_variable_payload(request, json_key, json_value):
    return {
        NAME_KEY: "TEST_JSON_VAR",
        VALUE_KEY: "{{\"{key}\": {value}}}".format(key=json_key, value=json_value),
        DESERIALIZE_JSON_KEY: True
    }


@pytest.fixture
def existing_variable(request, variables_resource_uri, variable_payload, json_header):
    uri = "{base_uri}/{variable_id}".format(base_uri=variables_resource_uri, variable_id=variable_payload[NAME_KEY])
    payload = json.dumps({key: value for (key, value) in variable_payload.items() if key != NAME_KEY})
    post_resp = requests.post(uri, data=payload, headers=json_header)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE

    def teardown_variable():
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code in [DELETE_RESPONSE_SUCCESS_CODE, NOT_FOUND_RESPONSE_CODE]
    request.addfinalizer(teardown_variable)
    return variable_payload


@pytest.fixture
def existing_json_variable(request, variables_resource_uri, json_variable_payload, json_header):
    uri = "{base_uri}/{variable_id}".format(
        base_uri=variables_resource_uri,
        variable_id=json_variable_payload[NAME_KEY]
    )
    payload = json.dumps({key: value for (key, value) in json_variable_payload.items() if key != NAME_KEY})
    post_resp = requests.post(uri, data=payload, headers=json_header)
    assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE

    def teardown_variable():
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code in [DELETE_RESPONSE_SUCCESS_CODE, NOT_FOUND_RESPONSE_CODE]
    request.addfinalizer(teardown_variable)
    return json_variable_payload


class TestPostVariablesResource:
    def test_post_variables_works_with_variables(
            self,
            variables_resource_uri,
            variable_payload,
            json_variable_payload,
            json_header
    ):
        data = [variable_payload, json_variable_payload]
        post_resp = requests.post(variables_resource_uri, data=json.dumps(data), headers=json_header)
        assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
        body = post_resp.json()
        regular_var = [var for var in body if var[NAME_KEY] == variable_payload[NAME_KEY]]
        assert len(regular_var) == 1
        assert regular_var[0][NAME_KEY] == variable_payload[NAME_KEY]
        assert regular_var[0][VALUE_KEY] == variable_payload[VALUE_KEY]
        assert regular_var[0][DESERIALIZE_JSON_KEY] == variable_payload[DESERIALIZE_JSON_KEY]
        json_var = [var for var in body if var[NAME_KEY] == json_variable_payload[NAME_KEY]]
        assert len(json_var) == 1
        assert json_var[0][NAME_KEY] == json_variable_payload[NAME_KEY]
        assert json_var[0][VALUE_KEY] == json.loads(json_variable_payload[VALUE_KEY])
        assert json_var[0][DESERIALIZE_JSON_KEY] == json_variable_payload[DESERIALIZE_JSON_KEY]
        for variable in data:
            delete_resp = requests.delete("{variables_resource_uri}/{var_name}".format(
                variables_resource_uri=variables_resource_uri,
                var_name=variable[NAME_KEY]
            ))
            assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

    def test_post_variables_will_not_post_empty_data(self, variables_resource_uri, json_header):
        post_resp = requests.post(variables_resource_uri, data=json.dumps([]), headers=json_header)
        assert post_resp.status_code == BAD_REQUEST_RESPONSE_CODE


class TestGetVariablesResource:
    def test_get_variables_works_with_variable(self, variables_resource_uri, existing_variable):
        get_resp = requests.get(variables_resource_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert len(body) == 1
        assert body[0][NAME_KEY] == existing_variable[NAME_KEY]
        assert body[0][VALUE_KEY] == existing_variable[VALUE_KEY]
        assert body[0][DESERIALIZE_JSON_KEY] == existing_variable[DESERIALIZE_JSON_KEY]

    def test_get_variables_works_with_json_variable(
            self,
            variables_resource_uri,
            existing_json_variable,
            json_key,
            json_value
    ):
        get_resp = requests.get(variables_resource_uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert len(body) == 1
        assert body[0][NAME_KEY] == existing_json_variable[NAME_KEY]
        assert body[0][VALUE_KEY][json_key] == json_value
        assert body[0][DESERIALIZE_JSON_KEY] == existing_json_variable[DESERIALIZE_JSON_KEY]


class TestGetVariableByIdResource:
    def test_get_variable_by_id_works_with_variable(self, variables_resource_uri, existing_variable):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id=existing_variable[NAME_KEY]
        )
        get_resp = requests.get(uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert body[NAME_KEY] == existing_variable[NAME_KEY]
        assert body[VALUE_KEY] == existing_variable[VALUE_KEY]
        assert body[DESERIALIZE_JSON_KEY] == existing_variable[DESERIALIZE_JSON_KEY]

    def test_get_variable_by_id_works_with_json_variable(
            self,
            variables_resource_uri,
            existing_json_variable,
            json_key,
            json_value
    ):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id=existing_json_variable[NAME_KEY]
        )
        params = {DESERIALIZE_JSON_KEY: existing_json_variable[DESERIALIZE_JSON_KEY]}
        get_resp = requests.get(uri, params=params)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert body[NAME_KEY] == existing_json_variable[NAME_KEY]
        assert body[VALUE_KEY][json_key] == json_value
        assert body[DESERIALIZE_JSON_KEY] == existing_json_variable[DESERIALIZE_JSON_KEY]

    def test_get_variable_by_id_throws_404(self, variables_resource_uri):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id="test"
        )
        get_resp = requests.get(uri)
        assert get_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestDeleteVariableByIdResource:
    def test_delete_variable_by_id_works_with_variable(self, variables_resource_uri, existing_variable):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id=existing_variable[NAME_KEY]
        )
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

    def test_delete_variable_by_id_works_with_json_variable(
            self,
            variables_resource_uri,
            existing_json_variable
    ):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id=existing_json_variable[NAME_KEY]
        )
        params = {DESERIALIZE_JSON_KEY: existing_json_variable[DESERIALIZE_JSON_KEY]}
        delete_resp = requests.delete(uri, params=params)
        assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

    def test_delete_variable_by_id_throws_404(self, variables_resource_uri):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id="test"
        )
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == NOT_FOUND_RESPONSE_CODE


class TestPostVariableByIdResource:
    def test_post_variable_by_id_works_with_variable(self, variables_resource_uri, variable_payload, json_header):
        uri = "{base_uri}/{variable_id}".format(base_uri=variables_resource_uri, variable_id=variable_payload[NAME_KEY])
        payload = json.dumps({key: value for (key, value) in variable_payload.items() if key != NAME_KEY})
        post_resp = requests.post(uri, data=payload, headers=json_header)
        assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
        get_resp = requests.get(uri)
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert body[NAME_KEY] == variable_payload[NAME_KEY]
        assert body[VALUE_KEY] == variable_payload[VALUE_KEY]
        assert body[DESERIALIZE_JSON_KEY] == variable_payload[DESERIALIZE_JSON_KEY]
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

    def test_post_variable_by_id_works_with_variable(self, variables_resource_uri, json_variable_payload, json_header):
        uri = "{base_uri}/{variable_id}".format(
            base_uri=variables_resource_uri,
            variable_id=json_variable_payload[NAME_KEY]
        )
        payload = json.dumps({key: value for (key, value) in json_variable_payload.items() if key != NAME_KEY})
        post_resp = requests.post(uri, data=payload, headers=json_header)
        assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
        get_resp = requests.get(uri, params={DESERIALIZE_JSON_KEY: json_variable_payload[DESERIALIZE_JSON_KEY]})
        assert get_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_resp.json()
        assert body[NAME_KEY] == json_variable_payload[NAME_KEY]
        assert body[VALUE_KEY] == json.loads(json_variable_payload[VALUE_KEY])
        assert body[DESERIALIZE_JSON_KEY] == json_variable_payload[DESERIALIZE_JSON_KEY]
        delete_resp = requests.delete(uri)
        assert delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE

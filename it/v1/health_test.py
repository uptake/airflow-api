import pytest
import requests

from airflowapi.constants import GET_RESPONSE_SUCCESS_CODE
from airflowapi.v1.api_blueprint import HEALTH_ROUTE


@pytest.fixture(scope="module")
def health_resource_uri(request, api_uri):
    return "{api_uri}{health_route}".format(api_uri=api_uri, health_route=HEALTH_ROUTE)


class TestHealthResource:

    def test_health_resource(self, health_resource_uri):

        resp = requests.get(health_resource_uri)
        assert resp.status_code == GET_RESPONSE_SUCCESS_CODE
        assert resp.json()["health"] == "ok"

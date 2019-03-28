import requests

from airflowapi.constants import \
    POST_RESPONSE_SUCCESS_CODE, \
    GET_RESPONSE_SUCCESS_CODE, \
    DELETE_RESPONSE_SUCCESS_CODE, \
    CONFLICT_RESPONSE_CODE, \
    BAD_REQUEST_RESPONSE_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    PUT_RESPONSE_SUCCESS_CODE
from airflowapi.v1.dag_files import FILE_KEY


class TestGetDagFilesResource:
    def test_get_dag_files_works_with_dag(self, test_dag_file_on_server, dag_files_resource_uri):
        get_dag_files_resp = requests.get(dag_files_resource_uri)
        assert get_dag_files_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_dag_files_resp.json()
        assert len(body) == 1
        assert body[0][FILE_KEY] == test_dag_file_on_server.filename

    def test_get_dag_files_works_without_dag(self, dag_files_resource_uri):
        get_dag_files_resp = requests.get(dag_files_resource_uri)
        assert get_dag_files_resp.status_code == GET_RESPONSE_SUCCESS_CODE
        body = get_dag_files_resp.json()
        assert len(body) == 0


class TestPostDagFilesResource:
    def test_post_dag_file_works(self, dag_files_resource_uri, test_dag_file):
        try:
            post_resp = requests.post(dag_files_resource_uri, files=test_dag_file.post_data)
            assert post_resp.status_code == POST_RESPONSE_SUCCESS_CODE
            get_dag_files_resp = requests.get(dag_files_resource_uri)
            assert get_dag_files_resp.status_code == GET_RESPONSE_SUCCESS_CODE
            body = get_dag_files_resp.json()
            assert len(body) == 1
            assert body[0][FILE_KEY] == test_dag_file.filename
            delete_resp = requests.delete(dag_files_resource_uri, params={"file": test_dag_file.filename})
            assert(delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE)
        except Exception as e:
            requests.delete(dag_files_resource_uri, params={"file": test_dag_file.filename})
            raise e

    def test_post_dag_file_will_not_overwrite(self, dag_files_resource_uri, test_dag_file_on_server):
        post_resp = requests.post(dag_files_resource_uri, files=test_dag_file_on_server.post_data)
        assert post_resp.status_code == CONFLICT_RESPONSE_CODE

    def test_post_dag_file_will_not_upload_wrong_format(
            self,
            dag_files_resource_uri
    ):
        bad_file_format = {'file': ("test.txt", "123")}
        post_resp = requests.post(dag_files_resource_uri, files=bad_file_format)
        assert post_resp.status_code == BAD_REQUEST_RESPONSE_CODE

    def test_post_dag_file_will_not_upload_empty_file(
            self,
            dag_files_resource_uri
    ):
        bad_file = {'file': ("test.txt", "")}
        post_resp = requests.post(dag_files_resource_uri, files=bad_file)
        assert post_resp.status_code == BAD_REQUEST_RESPONSE_CODE


class TestDeleteDagFilesResource:
    def test_delete_dag_file_works(self, dag_files_resource_uri, test_dag_file_on_server):
        delete_resp = requests.delete(dag_files_resource_uri, params={"file": test_dag_file_on_server.filename})
        assert(delete_resp.status_code == DELETE_RESPONSE_SUCCESS_CODE)

    def test_delete_dag_file_throws_404(self, dag_files_resource_uri):
        delete_resp = requests.delete(dag_files_resource_uri, params={"file": "test.py"})
        assert(delete_resp.status_code == NOT_FOUND_RESPONSE_CODE)

    def test_delete_dag_file_throws_will_not_delete_wrong_format(self, dag_files_resource_uri):
        delete_resp = requests.delete(dag_files_resource_uri, params={"file": "test.txt"})
        assert(delete_resp.status_code == BAD_REQUEST_RESPONSE_CODE)

    def test_delete_dag_file_throws_will_throw_400_for_empty_filename(self, dag_files_resource_uri):
        delete_resp = requests.delete(dag_files_resource_uri, params={"file": ""})
        assert(delete_resp.status_code == BAD_REQUEST_RESPONSE_CODE)


class TestPutDagFilesResource:
    def test_put_dag_file_works(self, dag_files_resource_uri, test_dag_file_on_server):
        put_resp = requests.put(dag_files_resource_uri, files=test_dag_file_on_server.post_data)
        assert(put_resp.status_code == PUT_RESPONSE_SUCCESS_CODE)

    def test_put_dag_file_throws_404(self, dag_files_resource_uri):
        put_resp = requests.put(dag_files_resource_uri, files={"file": ("test.py", "123")})
        assert(put_resp.status_code == NOT_FOUND_RESPONSE_CODE)

    def test_put_dag_file_will_not_update_wrong_format(self, dag_files_resource_uri):
        put_resp = requests.put(dag_files_resource_uri, files={"file": ("test", "123")})
        assert(put_resp.status_code == BAD_REQUEST_RESPONSE_CODE)

    def test_put_dag_file_will_throw_400_for_empty_file(self, test_dag_file_on_server, dag_files_resource_uri):
        put_resp = requests.put(dag_files_resource_uri, files={"file": ("", "123")})
        assert(put_resp.status_code == BAD_REQUEST_RESPONSE_CODE)




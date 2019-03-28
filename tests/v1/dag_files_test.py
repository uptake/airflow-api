
from airflowapi.v1.dag_files import check_for_allowed_file


class TestDagFiles:

    def test_check_for_allowed_file_with_allowed_file(self):
        assert check_for_allowed_file('test.py')

    def test_check_for_allowed_file_with_wrong_extension(self):
        assert not check_for_allowed_file('test.txt')

    def test_check_for_allowed_file_with_no_extension(self):
        assert not check_for_allowed_file('test')

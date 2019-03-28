from airflow.models import DagModel
from airflowapi.v1.dags import _process_dag_to_response, DAG_ID_KEY, IS_PAUSED_KEY, FILE_LOCATION_KEY
from datetime import datetime


class TestDags:

    def test_process_dag_to_response(self):
        dag_id = "test_dag"
        fileloc = "my_file"
        is_paused = True
        dag = DagModel(
            dag_id=dag_id,
            is_paused=is_paused,
            is_active=True,
            is_subdag=False,
            last_scheduler_run=datetime.now(),
            last_pickled=datetime.now(),
            last_expired=datetime.now(),
            scheduler_lock=False,
            pickle_id=1,
            fileloc=fileloc,
            owners="test"
        )
        processed_response = _process_dag_to_response(dag)
        assert dag_id == processed_response[DAG_ID_KEY]
        assert fileloc == processed_response[FILE_LOCATION_KEY]
        assert is_paused == processed_response[IS_PAUSED_KEY]


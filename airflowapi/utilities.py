import contextlib
from airflow import settings
from airflow.models import DagModel


@contextlib.contextmanager
def airflow_sql_alchemy_session():
    session = settings.Session()
    try:
        yield session
    finally:
        session.close()


def check_for_dag_id(dag_id):
    with airflow_sql_alchemy_session() as session:
        return session.query(DagModel).filter(
            DagModel.dag_id == dag_id
        ).first()

FROM airflow-api:base-image

USER test_user
COPY script/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
RUN mkdir /usr/local/airflow/plugins
COPY plugin.py /usr/local/airflow/plugins/plugin.py
RUN echo ${BUILD_ENVIRONMENT_NETWORK}
COPY ./ $CI_USER_HOME/airflowapi

USER root
RUN find $CI_USER_HOME/airflowapi | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

RUN find $CI_USER_HOME  -type f -or -type d -exec chown test_user:test_user {} \;
#RUN find $CI_USER_HOME -type d -exec chown test_user:test_user {} \;

USER test_user
RUN $(which pip) install --user $CI_USER_HOME/airflowapi


EXPOSE 8080 5555 8793
#USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh", "webserver"]

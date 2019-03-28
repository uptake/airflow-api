# The Airflow API
This is a package for enabling access to an Airflow (https://airflow.apache.org/) service via a RESTful interface. 
It is currently only functional with a LocalExecutor.

## Integration with an Existing Airflow Service
In order to integrate this package with an existing Airflow service you can either:

1. Copy the entirety of the source code at `airflowapi` and the `plugins.py` file into a folder 
at `$AIRFLOW_HOME/plugins` in the airflow service.
        
    ``` 
    mkdir -p $AIRFLOW_HOME/plugins && cp -r airflowapi $AIRFLOW_HOME/plugins && cp plugins.py $AIRFLOW_HOME/plugins
    ```
2. Pip install the `airflowapi` package into the same python distribution that is running the airflow service and copy 
the `plugins.py` file into a folder at `$AIRFLOW_HOME/plugins` in the airflow service

    ```
    pip install . && mkdir -p $AIRFLOW_HOME/plugins && cp plugins.py $AIRFLOW_HOME/plugins
    ```
The api's documentation can be found at the `api/v1/doc` route of the airflow service.


# Development
In order to do development you will need a python 3.6 environment set up as your base python installation.

We encourage developers to understand and leverage either of the following to create a clean environment for 
development:
* [conda](https://docs.conda.io/en/latest/) via [Anaconda](https://www.anaconda.com/) 
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)

## Running Unit Tests
To run all tests simply run the following command:

    ./bin/run_tests.sh
    
## Running Integration Tests
This assumes you are developing on Mac OSX System. Development on other systems is currently not tested or documented.

You will need docker installed on your system in order to run these tests.

You will first need to build the base image used in testing. This helps speed up development by establishing system
values which aren't often changed. You can do so by running the following command:

    docker build -f AirflowTestEnvDockerfile -t "airflow-api:base-image" .

You will need to add the following to your /etc/hosts file:

    127.0.0.1       airflow-webserver
    
This can be done easily bu running the following command:

    sudo echo "127.0.0.1 airflow-webserver" >> /etc/hosts 
 
To run all tests simply run the following command:

    ./bin/run_integration_tests.sh
    
If you would like to run tests in debug mode you can run the following to spin up the docker images needed:

    ./docker-compose-wrapper.sh up
    
When you are done with the images you can spin them down with this command:

    ./docker-compose-wrapper.sh down

# Tested Application Configurations

The following are the tested application configurations which are confirmed to work:

| Package Version | Airflow Version | sql_alchemy_conn Protocol | worker_class Type | Executor      |
|-----------------|-----------------|---------------------------|-------------------|---------------|
| 1.1.0           | 1.10.1          | postgresql+psycopg2       | sync              | LocalExecutor |
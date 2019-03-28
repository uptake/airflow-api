#!/usr/bin/env bash

TRY_LOOP="20"

# Slugify user text is necessary for apache-airflow
export SLUGIFY_USES_TEXT_UNIDECODE=yes
echo "Docker network is set to ${BUILD_ENVIRONMENT_NETWORK}"

wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' airflow-webserver:8080/api/v1/health)" != "200" ]]; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(curl -i airflow-webserver:8080/api/v1/health)"
    echo "$(date) - waiting for $name... $j/$TRY_LOOP"
    sleep 5
  done
}

./docker-compose-wrapper.sh up
{
    wait_for_port "Airflow" "airflow-webserver" 8080
    pip install --user ".[test]"
    pytest it
    ./docker-compose-wrapper.sh down
} || {
    ./docker-compose-wrapper.sh down
    exit 1
}
#!/usr/bin/env bash
set -e
if [ "$@" != "up" ] && [ "$@" != "down" ]
then
    echo "acceptable params are up or down"
    exit 1
fi

defaultDockerNetworkName="airflow-api-network"
if [[ -z "${BUILD_ENVIRONMENT_NETWORK}" ]]; then
    echo "No Docker Network Detected. Using $defaultDockerNetworkName"
    dockerNetworkName=defaultDockerNetworkName
else
    echo "Docker Network Detected. Using $BUILD_ENVIRONMENT_NETWORK"
    dockerNetworkName="${BUILD_ENVIRONMENT_NETWORK}"
fi

export BUILD_ENVIRONMENT_NETWORK=${dockerNetworkName}
./bin/create-docker-network.sh ${dockerNetworkName}
if [ "$@" = "up" ]
then
    command="docker-compose -f $(pwd)/docker-compose-LocalExecutor.yml $@ --build -d"
elif [ "$@" = "down" ]
then
    command="docker-compose -f $(pwd)/docker-compose-LocalExecutor.yml $@"
fi

eval $command
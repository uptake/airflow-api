#!/usr/bin/env bash

echo "working on network $@"
if [[ $(docker network ls | grep "$@") = "" ]]; then
    echo "creating the docker network $@"
    docker network create "$@"
fi
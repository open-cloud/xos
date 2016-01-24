#!/bin/bash

MODE=`docker inspect --format '{{ .HostConfig.NetworkMode }}' $1  | tr -d '\n' | tr -d '\r'`
if [[ "$MODE" == "host" ]]; then
    echo -n "127.0.0.1"
else
    docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1 | tr -d '\n' | tr -d '\r'
fi


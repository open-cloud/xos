#!/bin/sh

docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1 | tr -d '\n' | tr -d '\r'


#!/bin/bash

dir=$(dirname "$(readlink -f "$0")")

ps_exists=$(docker ps | grep onward_test_db)
if [[ ! "${ps_exists}" -eq "" ]]; then
    docker stop onward_test_db
fi

docker run -d \
       --rm \
       --net=host \
       -e POSTGRES_USER=${PGUSER} \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       --name onward_test_db \
       postgres:12.2

sleep 2

ERRS=1
while [[ ! "${ERRS}" -eq "0" ]]; do
    ${dir}/install.sh
    ERRS=$?
done

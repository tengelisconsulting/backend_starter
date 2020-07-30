#!/bin/bash

SERVICE="$1"
MAIN="$2"
SERVICE_NAME=$(echo "${SERVICE}" | tr '[:lower:]' '[:upper:]')


if [[ "${MAIN}" == "" ]]; then
    MAIN="./workers/ez_worker_main.py"
elif [[ "${MAIN}" == "0" ]]; then
    MAIN="./workers/${SERVICE}/py/main.py"
fi
cp ${MAIN} ./workers/${SERVICE}/py/main.tmp.py

cp ./workers/ez.py ./workers/${SERVICE}/py/ez.py


cleanup() {
    rm ./workers/${SERVICE}/py/main.tmp.py
    rm ./workers/${SERVICE}/py/ez.py
}

trap "cleanup" 1 2 3 6
SERVICE_NAME=${SERVICE_NAME} \
            PORT=9004 \
            LISTEN_HOST=localhost \
            ./workers/${SERVICE}/py/main.tmp.py
cleanup

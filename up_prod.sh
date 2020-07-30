#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source ./env/prod.env

PIPE_SCALE=1                    # binary
BROKER_SCALE=1                  # arbitrary

GATEWAY_SCALE=1                 # binary
POSTGREST_SCALE=1               # binary

# workers
AUTH_PROVIDER_W_SCALE=1
AUTHENTICATE_W_SCALE=1
AUTHORIZE_W_SCALE=1
DB_W_SCALE=1


docker-compose up -d \
               --scale in_pipe=${PIPE_SCALE} \
               --scale worker_pipe=${PIPE_SCALE} \
               --scale broker_pipe=${PIPE_SCALE} \
               --scale broker=${BROKER_SCALE} \
               --scale gateway=${GATEWAY_SCALE} \
               --scale postgrest=${POSTGREST_SCALE} \
               --scale auth_provider_w=${AUTH_PROVIDER_W_SCALE} \
               --scale authenticate_w=${AUTHENTICATE_W_SCALE} \
               --scale authorize_w=${AUTHORIZE_W_SCALE} \
               --scale db_w=${DB_W_SCALE}

docker-compose logs --follow

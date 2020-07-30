#!/bin/sh

base_dir=$(dirname "$(readlink -f "$0")")
dcp_file=${base_dir}/../docker-compose.yaml

LUA_CODE_CACHE="off" docker-compose -f ${dcp_file} run --rm \
              -v ${base_dir}/lua:/app/lua \
              gateway

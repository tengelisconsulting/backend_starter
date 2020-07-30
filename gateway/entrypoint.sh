#!/bin/sh


env_sub() {
    val=$(eval "echo \"\$$1\"")
    sed_arg="s/\\\${$1}/${val}/"
    sed -i -e $sed_arg nginx/nginx.conf
}


main() {
    set -e

    cp nginx/nginx.template.conf nginx/nginx.conf
    env_sub GATEWAY_PORT
    env_sub GATEWAY_HOST
    env_sub LUA_CODE_CACHE
    env_sub PGST_HOST
    env_sub PGST_PORT
    env_sub WORKER_PROCS
    env_sub GIT_REV
    env_sub NEW_USER_RATE
    env_sub LOGIN_RATE
    env_sub GATEWAY_LOG_LEVEL

    openresty -p `pwd`/ -c nginx/nginx.conf

    tail -f logs/*.log
}


main

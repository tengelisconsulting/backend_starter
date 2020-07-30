#!/bin/sh


docker run -d \
       --rm \
       --net=host \
       -e POSTGRES_USER=${PGUSER} \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       -v "${DB_DIRNAME}:/var/lib/postgresql/data" \
       --name onward_dev_db \
       postgres:12.2

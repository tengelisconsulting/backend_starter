#!/bin/bash

bin_dir=$(dirname "$(readlink -f "$0")")

alias psql="psql -h ${PGHOST} -U ${PGUSER}"


psql -c "DROP SCHEMA public CASCADE;"
psql -c "DROP SCHEMA api CASCADE;"
psql -c "DROP SCHEMA sys CASCADE;"
psql -c "CREATE SCHEMA public;"

${bin_dir}/install.sh

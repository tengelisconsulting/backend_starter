#!/bin/bash

# TO SPECIFY A GIT REVISION AS AN UPGRADE TARGET,
# create the directory '/migrate/{FULL_GIT_REV}'.
# Inside this directory, if there exists a 'pre.sql' file,
# it will be run before this version of the DB is installed.
# Similarly with the file 'post.sql' in this directory


bin_dir=$(dirname "$(readlink -f "$0")")
DB_DIR=${bin_dir}/..

alias psql="psql -h ${PGHOST} -U ${PGUSER}"

CURRENT_REV=$(psql -t -c "SELECT git_rev FROM current_vsn;")

rev_upgrades_db() {
    TEST_REV=$1
    git merge-base --is-ancestor ${TEST_REV} ${CURRENT_REV}
    echo $?
}

do_install() {
    VSN=$1
    SHORT_GIT_REV=$(git rev-parse --short --verify ${VSN})
    echo ${SHORT_GIT_REV}
    docker run -it \
           --rm \
           --net=host \
           -e FORCE=1 \
           -e PGHOST=${PGHOST} \
           -e PGUSER=${PGUSER} \
           onwardapp/db:${SHORT_GIT_REV}
}

run_upgrade() {
    VSN=$1
    set -e
    echo "RUNNING UPGRADE ${VSN}"
    pre_script="${DB_DIR}/migrate/${VSN}/pre.sql"
    if [[ -f ${pre_script} ]]; then
        echo "RUNNING 'PRE' SCRIPT"
        psql -f ${pre_script}
    fi
    echo "RUNNING INSTALL"
    do_install ${VSN}
    post_script="${DB_DIR}/migrate/${VSN}/post.sql"
    if [[ -f ${post_script} ]]; then
        echo "RUNNING 'POST' SCRIPT"
        psql -f ${post_script}
    fi
}

main() {
    if [[ "${CURRENT_REV}" == "" ]]; then
        echo "NO INSTALLS LOGGED, PERFORM 'INSTALL' INSTEAD"
        exit 1
    fi

    ALL_REVS_ORDER=$(git log --format="%H" --reverse)
    UPGRADES=$(ls ${DB_DIR}/migrate)
    WILL_DO=""

    for upgrade in ${UPGRADES}; do
        should_perform=$(rev_upgrades_db ${upgrade})
        if [[ "${should_perform}" == "1" ]]; then
            WILL_DO="${upgrade} ${WILL_DO}"
        fi
    done

    for rev in ${ALL_REVS_ORDER}; do
        if [[ "$(grep ${rev} <<< ${WILL_DO})" != "" ]]; then
            run_upgrade ${rev}
        fi
    done
}

main

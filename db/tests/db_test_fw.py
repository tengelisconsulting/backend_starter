#!/usr/bin/env python3

import asyncpg
import logging
import os
import requests
import subprocess

from types import SimpleNamespace


DB_TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_USER = "testing@tengelisconsulting.com"
TEST_USER_ID = ""


def get_timezone() -> str:
    url = "https://ipapi.co/timezone"
    try:
        with requests.Session() as s:
            res = s.get(url)
            assert res.ok
            return res.text
    except requests.exceptions.ConnectionError:
        logging.error("failed to get actual timezone")
    return "America/Vancouver"


TIMEZONE = get_timezone()


class TestEnv(SimpleNamespace):
    timezone: str
    db: asyncpg.pool.Pool


async def new_env() -> TestEnv:
    return TestEnv(
        db=await connect_db(),
        timezone=TIMEZONE,
    )


async def destroy_env(t: TestEnv) -> None:
    await t.db.close()
    return


async def connect_db() -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(
                user=os.environ["PGUSER"],
                password=os.environ["PGPASSWORD"],
                database=os.environ["PGDB"],
                host=os.environ["PGHOST"],
            )


async def install_db(t: TestEnv) -> None:
    logging.info("dropping database...")
    await t.db.execute("DROP SCHEMA IF EXISTS public CASCADE")
    await t.db.execute("DROP SCHEMA IF EXISTS api CASCADE")
    await t.db.execute("DROP SCHEMA IF EXISTS sys CASCADE")
    await t.db.execute("CREATE SCHEMA public")
    install_bin = os.path.abspath(
        os.path.join(DB_TEST_DIR, "../bin", "install.sh"))
    subprocess.check_output(["ls", install_bin])
    res = subprocess.run([install_bin],
                         env=os.environ,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if res.returncode == 0:
        test_user_id = await t.db.fetchval("""
        SELECT user_id
          FROM ac_user
         WHERE email_lower = $1
        """, TEST_USER)
        global TEST_USER_ID
        TEST_USER_ID = str(test_user_id)
        logging.info("db install success")
        return
    logging.error(res.stderr.decode("utf-8"))
    logging.error("tests failed because db install failed")
    raise Exception("failed to install db")


def db_test(_fn=None, *, clean_db=False, run_first=[]):
    def dec(fn):
        async def impl_fn(t: TestEnv):
            return await fn(t)
        impl_fn.clean_db = clean_db
        impl_fn.is_test = True
        impl_fn.run_first = run_first
        return impl_fn
    if _fn is None:
        return dec
    return dec(_fn)

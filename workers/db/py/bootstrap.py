import asyncio
import logging
import time
from typing import List

import asyncpg

import ez

from app import app
import dynamic
from env import ENV


INIT_ATTEMPTS = 5


def wrap_query(query: str) -> str:
    sql = """
      WITH inside AS (
        {}
      )
      SELECT json_agg(inside)
        FROM inside
    """
    return sql.format(query)


@ez.endpoint(route=b"/text_slow")
async def test_slow():
    logging.info("got req, will sleep")
    await asyncio.sleep(2)
    logging.info("replying")
    return [b"OK", time.time()]


@ez.endpoint(route=b"/fetch/json")
async def fetch_json(
        sql: str,
        bindargs: List = []
):
    wrapped_sql = wrap_query(sql)
    async with app.db_pool.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(wrapped_sql, *bindargs)
            return (b"OK", res)


@ez.endpoint(route=b"/fetch/val")
async def fetch_val(
        sql: str,
        bindargs: List = []
):
    async with app.db_pool.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(sql, *bindargs)
            return (b"OK", res)


@ez.endpoint(route=b"/exec")
async def execute(
        sql: str,
        bindargs: List = []
):
    async with app.db_pool.acquire() as con:
        async with con.transaction():
            res = await con.execute(sql, *bindargs)
            return (b"OK", res)


async def tester():
    logging.info("tester")
    return (b"OK", {})


async def dynamic_routes():
    return await dynamic.load_dynamic_routes()


async def init() -> None:
    attempt = 1
    backoff_s = 1
    while attempt < INIT_ATTEMPTS:
        try:
            pool = await asyncpg.create_pool(
                user=ENV.PGUSER,
                password=ENV.PGPASSWORD,
                database=ENV.PGDB,
                host=ENV.PGHOST,
            )
            logging.info("connected to db")
            app.db_pool = pool
            break
        except Exception as e:
            logging.exception(e)
            attempt = attempt + 1
            logging.error("attempt connect in %s s", backoff_s)
            await asyncio.sleep(backoff_s)
            backoff_s = backoff_s * 2
    return


async def close() -> None:
    await app.db_pool.close()
    return

import asyncio
import json
import logging
import os
from typing import List

import asyncpg

import framework as fmk


PGUSER = os.environ["PGUSER"]
PGPASSWORD = os.environ["PGPASSWORD"]
PGDB = os.environ["PGDB"]
PGHOST = os.environ["PGHOST"]


DB_POOL: asyncpg.pool.Pool
INIT_ATTEMPTS = 3


async def init() -> None:
    attempt = 1
    backoff_s = 1
    global DB_POOL
    while attempt < INIT_ATTEMPTS:
        try:
            DB_POOL = await asyncpg.create_pool(
                user=PGUSER,
                password=PGPASSWORD,
                database=PGDB,
                host=PGHOST,
            )
            logging.info("connected to db")
            break
        except Exception as e:
            logging.exception(e)
            attempt = attempt + 1
            logging.error("attempt connect in %s s", backoff_s)
            await asyncio.sleep(backoff_s)
            backoff_s = backoff_s * 2
    return


def wrap_query(query: str) -> str:
    sql = """
      WITH inside AS (
        {}
      )
      SELECT json_agg(inside)
        FROM inside
    """
    return sql.format(query)


async def fetch(sql: str, bindargs: List = []):
    wrapped_sql = wrap_query(sql)
    async with DB_POOL.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(wrapped_sql, *bindargs)
            return json.loads(res)


async def fetch_nowrap(sql: str,
                       bindargs: List = [],
                       res_is_json: bool = False):
    async with DB_POOL.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(sql, *bindargs)
            if res_is_json:
                return json.loads(res)
            return res


async def get_email_onward_id(msg_type: str) -> str:
    res = await fetch("""
    SELECT cl.adhoc->>'onward_id' onward_id
      FROM user_email_comms_log cl
      JOIN ac_user u
        ON u.user_id = cl.user_id
     WHERE u.email_lower = $1
       AND cl.msg_type = $2::USER_MSG_T
    """, [fmk.TEST_EMAIL, msg_type])
    assert len(res) == 1
    return res[0]["onward_id"]

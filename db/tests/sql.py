import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple

from db_test_fw import TestEnv


class FnArg(NamedTuple):
    name: str
    val: Any
    type_s: str


def wrap_query(query: str) -> str:
    sql = """
      WITH inside AS (
        {}
      )
      SELECT json_agg(inside)
        FROM inside
    """
    return sql.format(query)


async def ad_hoc(
        t: TestEnv,
        sql: str,
        bindargs: List[Any]
) -> Dict:
    sql = wrap_query(sql)
    async with t.db.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(sql, *bindargs)
            if res:
                return json.loads(res)
            return res


async def call_fn(
        t: TestEnv,
        fn_name: str,
        args: List[Tuple]
) -> Dict:
    args1: List[FnArg] = [FnArg(*arg) for arg in args]
    inside_sql = ",\n ".join([
        f"{args1[i].name} => ${i + 1}::{args1[i].type_s}"
        for i in range(len(args1))
    ])
    sql = f"""
  SELECT {fn_name}(
         {inside_sql}
         )
"""
    query_params = [arg[1] for arg in args1]
    sql = wrap_query(sql)
    async with t.db.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(sql, *query_params)
            if res:
                unqualified_name = fn_name.split(".")[-1]
                return json.loads(res)[0][unqualified_name]
            return res

import asyncio
import logging
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple

from asyncpg import Record

from app import app


SYS_SCHEMA_NAME = "sys"


class FnArg(NamedTuple):
    name: str
    type: str


class FnRecord(NamedTuple):
    name: str
    args: List[FnArg]


async def fetch_sys_functions() -> List[Record]:
    sql = """
      SELECT p.proname fn_name,
             pg_get_function_arguments(p.oid) args
      FROM pg_proc p INNER JOIN pg_namespace ns ON (p.pronamespace = ns.oid)
      WHERE ns.nspname = $1;
    """
    async with app.db_pool.acquire() as con:
        async with con.transaction():
            return await con.fetch(sql, SYS_SCHEMA_NAME)
    return


def create_db_proc_sql(r: FnRecord):
    args = sorted(r.args, key=lambda arg: arg.name)
    args_sql = ",\n    ".join([
        f"{args[i].name} => ${i + 1}::{args[i].type}"
        for i in range(len(args))
    ])
    sql = f"""
  SELECT {SYS_SCHEMA_NAME}.{r.name}(
    {args_sql}
  )
    """
    # logging.debug("generated %s as: %s", r.name, sql)
    return sql


async def execute_db_proc(sql: str, bindargs: List):
    async with app.db_pool.acquire() as con:
        async with con.transaction():
            res = await con.fetchval(sql, *bindargs)
            return (b"OK", res)
    return


def create_endpoint(r: FnRecord) -> Tuple[bytes, Callable]:
    proc_sql = create_db_proc_sql(r)

    async def handler(**kwargs):
        args = [arg[1] for arg in
                sorted(list(kwargs.items()), key=lambda arg: arg[0])]
        return await execute_db_proc(proc_sql, args)
    handler.__name__ = r.name
    path = b"/" + r.name.encode("utf-8")
    return path, handler


def load_record(r: Record) -> FnRecord:
    fn_name = r.get("fn_name")
    args = [s.strip() for s in r.get("args").split(",")]

    def to_fn_arg(arg_str: str) -> FnArg:
        parts = arg_str.split(" ")
        return FnArg(name=parts[0], type=parts[1])
    return FnRecord(
        name=fn_name,
        args=[to_fn_arg(arg) for arg in args]
    )


async def load_dynamic_routes():
    routes = {}
    records = await fetch_sys_functions()
    fnrs = [load_record(r) for r in records]
    for fnr in fnrs:
        route, handler = create_endpoint(fnr)
        routes[route] = handler
    return routes

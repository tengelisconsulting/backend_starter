#!/usr/bin/env python3

import asyncio
import logging
import inspect
import os
import pkgutil
import sys
import time
from typing import Any
from typing import List

import db_test_fw


def load_tests() -> List[Any]:
    modules = [
        finder.find_module(name).load_module(name)
        for finder, name, _ispkg
        in pkgutil.walk_packages([db_test_fw.DB_TEST_DIR])
    ]
    fns_by_module = [{
        "mod_name": m.__name__,
        "members": inspect.getmembers(m, inspect.isfunction)
    } for m in modules]
    for m in fns_by_module:
        m["members"] = [fn for fn in m["members"]
                        if getattr(fn[1], "is_test", None)]
    return [m for m in fns_by_module if len(m["members"])]


async def rebuild_env(t: db_test_fw.TestEnv = None) -> db_test_fw.TestEnv:
    if t:
        await db_test_fw.destroy_env(t)
    t = await db_test_fw.new_env()
    return t


async def main():
    logging.basicConfig(level=logging.INFO)
    target_mod = sys.argv[1] if len(sys.argv) > 1 else None
    logging.info("running target module -> %s", target_mod)
    target_db = os.environ["PGHOST"]
    confirmation = input("THESE TESTS WILL DESTROY THE DATABASE "
                         f"AT '{target_db}' - PROCEED? (y/n) ")
    if confirmation != "y":
        return
    t = None
    con_attempts = 5
    attempt = 0
    while not t:
        logging.info("attempt to connect...")
        try:
            t = await rebuild_env()
        except Exception as e:
            attempt = attempt + 1
            if attempt < con_attempts:
                logging.error("failed to connect - %s", e)
                time.sleep(2)
            else:
                logging.exception(e)
                raise(e)
    test_modules = load_tests()
    if target_mod:
        test_modules = [m for m in test_modules if m["mod_name"] == target_mod]
    for test_m in test_modules:
        logging.info("-------- TESTING '%s' ------", test_m["mod_name"])
        for test in test_m["members"]:
            if getattr(test[1], "clean_db", None):
                logging.info("installing db...")
                await db_test_fw.install_db(t)
                t = await rebuild_env(t)
            logging.info("running - %s", test[0])
            await test[1](t)
            logging.info("success")
        logging.info("-------- '%s' success ------", test_m["mod_name"])
    pass


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3

import asyncio
import inspect
import json
from json import JSONDecodeError
import logging
import os
import pkgutil
from typing import Any
from typing import Callable
from typing import Dict

import ez_arch_worker.api as ez_worker
from ez_arch_worker.api import Frames

import bootstrap


DIR = os.path.dirname(os.path.realpath(__file__))

LISTEN_HOST: str = os.environ.get("LISTEN_HOST", "localhost")
PORT: int = int(os.environ.get("PORT", 9004))
SERVICE_NAME: bytes = os.environ.get("SERVICE_NAME", "").encode("utf-8")

POLL_INTERVAL_MS: int = int(os.environ.get("POLL_INTERVAL_MS", 3000))

ROUTES: Dict[bytes, Callable] = {}


def setup_logging() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format=f"%(asctime)s.%(msecs)03d "
        "%(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return


async def reset() -> None:
    if getattr(bootstrap, "close", None):
        await getattr(bootstrap, "close")()
    await bootstrap.init()
    await load_dynamic_routes()
    return


async def handler(frames: Frames) -> Frames:
    # structure of req is [ cmd: str, args: json ].  Args must be dict.
    # structure of res is [ ok: b"OK" or b"ERR", body: json ]
    logging.debug("handling frames: %s", frames)
    cmd = frames[0]
    if cmd == b"RESET":
        asyncio.create_task(reset())
        return [b"OK", b"{}"]
    if cmd not in ROUTES:
        return [b"ERR", json.dumps({
            "code": 401,
            "msg": "{} not found".format(str(cmd)),
        }).encode("utf-8")]
    body: Dict
    try:
        if frames[1] == b"":
            body = {}
        else:
            body = json.loads(frames[1])
    except JSONDecodeError as e:
        logging.exception("body decode failed: %s", e)
        return [b"ERR", json.dumps({
            "code": 400,
            "msg": "body parse failed"
        }).encode("utf-8")]
    try:
        logging.info("%s", str(cmd))
        handler: Any = ROUTES[cmd]
        res = await handler(**body)
    except Exception as e:
        logging.exception("worker handler failed: %s", e)
        return [b"ERR", json.dumps({
            "code": 500,
            "msg": "service error",
        }).encode("utf-8")]
    res_body = json.dumps(res[1]).encode("utf-8") if res else b""
    return [res[0], res_body]


def define_routes() -> None:
    modules = [
        finder.find_module(name).load_module(name)
        for finder, name, _ispkg
        in pkgutil.walk_packages([DIR])
    ]
    mappings = [(getattr(fn, "route"), fn) for m in modules
                for (name, fn) in inspect.getmembers(m, inspect.isfunction)
                if getattr(fn, "route", None)]
    for route, fn in mappings:
        assert type(route) == bytes
        ROUTES[route] = fn
    logging.info("LOADED ROUTES:\n%s",
                 b"\n".join(list(ROUTES.keys())).decode('utf-8'))
    return


async def load_dynamic_routes() -> None:
    if not hasattr(bootstrap, "dynamic_routes"):
        return
    defs = await bootstrap.dynamic_routes()  # type: ignore
    for route, fn in defs.items():
        ROUTES[route] = fn
    logging.info("LOADED DYNAMIC ROUTES:\n%s",
                 b"\n".join(list(defs.keys())).decode("utf-8"))
    return


async def run_loop():
    logging.info("startup success %s", SERVICE_NAME)
    await ez_worker.run_worker(
        service_name=SERVICE_NAME,
        handler=handler,
        listen_host=LISTEN_HOST,
        port=PORT,
        poll_interval_ms=POLL_INTERVAL_MS
    )
    return


async def main():
    setup_logging()
    logging.info("attempt startup %s...", SERVICE_NAME)
    define_routes()
    await bootstrap.init()
    await load_dynamic_routes()
    await run_loop()
    return


if __name__ == "__main__":
    asyncio.run(main())

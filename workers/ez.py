import functools
import json
import logging
from typing import Dict
import os

from ez_arch_worker.api import EzClient
from ez_arch_worker.api import new_client


EZ_INPUT_HOST: str = os.environ.get("EZ_INPUT_HOST", "localhost")
EZ_INPUT_PORT: int = int(os.environ.get("EZ_INPUT_PORT", 9000))


class EzRequester:
    client: EzClient

    async def r(
            self,
            service_name: bytes,
            path: bytes,
            body: Dict,
            die_on_err: bool = True
    ):
        frames = [service_name, path, json.dumps(body).encode("utf-8")]
        ok, res = await self.client.r(frames)
        if ok == b"ERR":
            logging.error("request %s::%s failed: %s",
                          service_name, path, res)
            if die_on_err:
                raise Exception(res)
            return (None, json.loads(res))
        return (json.loads(res), None)

    async def r_json(
            self,
            service_name: bytes,
            path: bytes,
            body: Dict,
            die_on_err: bool = True
    ):
        res, err = await self.r(service_name, path, body, die_on_err)
        if res and not err:
            res = json.loads(res)
        return res, err


async def new_requester() -> EzRequester:
    requester = EzRequester()
    requester.client = await new_client(EZ_INPUT_HOST, EZ_INPUT_PORT)
    return requester


def endpoint(route: bytes = b"/"):
    def wrap(_fn):
        @functools.wraps(_fn)
        def impl_fn(*args, **kwargs):
            return _fn(*args, **kwargs)
        impl_fn.route = route
        return impl_fn
    return wrap

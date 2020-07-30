import asyncio
import inspect
import json
import logging
import os
import subprocess
from typing import Dict
from typing import List
from types import SimpleNamespace

from ez_arch_worker.api import EzClient
from ez_arch_worker.api import new_client
import requests

DEFAULT_TZ: str = "Asia/Vientiane"
REQ_TIMEOUT_S: int = 6
HOST: str = os.environ.get("HOST", "localhost")
DAY_START_SUBJECT: str = "DAY_START"
EMAIL_POLL_INTERVAL_S: int = 10
EMAIL_TIMEOUT_S: int = 500
TEST_EMAIL: str = "testing@tengelisconsulting.com"
TEST_PW: str = "a1s2d3f4g5"
REQ_PORT: int = int(os.environ["GATEWAY_PORT"])
EZ_INPUT_PORT: int = int(os.environ["EZ_INPUT_PORT"])
EZ_WORKER_PORT_A: int = int(os.environ["EZ_WORKER_PORT_A"])

TEST_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..")
DB_RESET_BIN = os.path.join(TEST_DIR, "../db", "bin", "reset.sh")


def get_timezone() -> str:
    retries = 3
    url = "https://ipapi.co/timezone"
    with requests.Session() as s:
        res = None
        attempt = 0
        while True:
            attempt = attempt + 1
            try:
                res = s.get(url)
            except Exception as e:
                if attempt > retries:
                    raise e
                continue
            assert res.ok
            break
        print("loaded timezone: ", res.text)
        if res.text == "None":
            print("using default timezone: ", DEFAULT_TZ)
            return DEFAULT_TZ
        return res.text
    return


class TestEnv(SimpleNamespace):
    ez: EzClient = None
    http_con_s: str = "http://{}:{}".format(HOST, REQ_PORT)
    host: str = HOST
    timezone: str = get_timezone()
    s: requests.Session = requests.Session()


t = TestEnv()


def assert_eq(act, exp):
    if exp != act:
        msg = "{} did not equal expected {}".format(act, exp)
        logging.error(msg)
        raise TestFailure(msg, caller=inspect.stack()[1])


def run_shell_cmd(cmd: List[str]) -> None:
    res = subprocess.run(cmd,
                         env=os.environ,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if res.returncode != 0:
        logging.error(res.stderr.decode("utf-8"))
        raise TestFailure("shell cmd error", caller=inspect.stack()[1])
    return


async def clear_db():
    run_shell_cmd([DB_RESET_BIN])
    logging.info("restarting DB worker")
    await ez(b"DB", b"RESET", {})
    await asyncio.sleep(1)
    logging.info("db re-installed")
    return


async def ez(
        service: bytes,
        path: bytes,
        data: Dict = None
):
    assert type(service) == bytes
    assert type(path) == bytes
    ok, res = await t.ez.r([
        service,
        path,
        json.dumps(data).encode("utf-8") if data else b""])
    return ok, json.loads(res)


def req(
        path: str,
        method: str = "GET",
        data: Dict = None,
        exp_code: int = 200,
        headers: Dict = {}
):
    if data:
        data = json.dumps(data)
    res = t.s.request(
        method=method,
        url=t.http_con_s + path,
        data=data,
        headers=headers,
        timeout=REQ_TIMEOUT_S
    )
    if not res.status_code == exp_code:
        logging.error(res.text)
        msg = "request {} {} failed: {} - {}".format(
            method, path, res.status_code, res.text)
        raise TestFailure(msg, caller=inspect.stack()[1])
    if res.ok:
        return res.json()
    return res.text


def success() -> None:
    caller = inspect.stack()[1]
    mod = caller[1]
    fn = caller[3]
    logging.info("%s SUCCESS - %s", mod, fn)
    return


def create_session() -> None:
    res = req("/auth/authenticate/username-password", method="POST", data={
        "email": TEST_EMAIL,
        "password": TEST_PW,
    })
    token = res["session_token"]
    t.s.headers["Authorization"] = "Bearer: {}".format(token)
    return


async def reset(do_create_session: bool = False) -> None:
    t.ez = await new_client("127.0.0.1", EZ_INPUT_PORT)
    await clear_db()
    if do_create_session:
        create_session()
    return


def endpoint_test(_fn=None, *, url=""):
    def dec(fn):
        def impl_fn():
            return fn(url)
        impl_fn.endpoint_test = True
        impl_fn.endpoint_url = url
        return impl_fn
    if _fn is None:
        return dec
    return dec(_fn)


class TestFailure(Exception):
    def __init__(self, msg, caller=None):
        self.msg = msg
        if caller is None:
            caller = inspect.stack()[1]
        frame = caller[0]
        self.info = inspect.getframeinfo(frame)

    def __str__(self):
        return f"""

+------------ TESTS FAILED ------------+
{self.info.filename} '{self.info.function}' line {self.info.lineno}

{self.msg}

+--------------------------------------+
        """

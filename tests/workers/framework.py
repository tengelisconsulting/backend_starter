import asyncio
import inspect
import json
import logging
import os
import subprocess
import tempfile
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from types import SimpleNamespace

from cryptography.fernet import Fernet

from ez_arch_worker.api import new_client
from ez_arch_worker.api import EzClient
from ez_arch_worker.api import mock_router
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
DB_INSTALL_BIN = os.path.join(TEST_DIR, "../db", "bin", "install.sh")


def get_timezone() -> str:
    url = "https://ipapi.co/timezone"
    with requests.Session() as s:
        res = s.get(url)
        assert res.ok
        logging.info("loaded timezone: %s", res.text)
        if res.text == "None":
            logging.info("using default timezone: %s", DEFAULT_TZ)
            return DEFAULT_TZ
        return res.text
    return


class TestEnv(SimpleNamespace):
    ez: EzClient = None
    http_con_s: str = "http://{}:{}".format(HOST, REQ_PORT)
    host: str = HOST
    timezone: str = ""
    s: requests.Session = requests.Session()
    mock_router = None


t = TestEnv()


async def reset(do_clear_db=True) -> None:
    logging.info("resetting")
    global t
    if t.mock_router:
        t.mock_router.cancel()
    t = TestEnv()
    t.ez = await new_client("127.0.0.1", EZ_INPUT_PORT)
    t.timezone = get_timezone()
    t.mock_router = mock_router.get_mock_router(
        ez_input_port=EZ_INPUT_PORT,
        ez_worker_port=EZ_WORKER_PORT_A
    )
    if do_clear_db:
        await clear_db()
    return


def ez_ok(data):
    return [b"OK", json.dumps(data).encode("utf-8")]


async def run_mock_ez(
        service_name: bytes,
        endpoints: Dict[Tuple[bytes, bytes], Callable]) -> None:
    if t.mock_router and t.mock_router.is_running():
        await t.mock_router.close()
    handler = mock_router.endpoint_mock(endpoints)

    def wrapped_handler(frames):
        try:
            return handler(frames)
        except Exception as e:
            logging.error("A MOCKED EZ HANDLER CRASHED")
            asyncio.get_event_loop().stop()
            raise(e)

    await t.mock_router.start(service_name, wrapped_handler)
    return


def assert_eq(act, exp):
    if exp != act:
        msg = "{} did not equal expected {}".format(act, exp)
        logging.error(msg)
        raise TestFailure(msg, caller=inspect.stack()[1])


async def leave() -> None:
    if t.ez:
        await t.ez.close()
    if t.mock_router:
        t.mock_router.cancel()
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
    run_shell_cmd(["psql", "-c", "DROP SCHEMA IF EXISTS PUBLIC CASCADE"])
    run_shell_cmd(["psql", "-c", "CREATE SCHEMA PUBLIC"])
    run_shell_cmd([DB_INSTALL_BIN])
    logging.info("restarting DB worker")
    await ez(b"DB", b"RESET", {})
    await asyncio.sleep(1)
    logging.info("db re-installed")
    return


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

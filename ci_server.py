#!/usr/bin/env python3

import asyncio
import logging
import os
import re
import subprocess
from typing import Dict

from aiohttp import web


LISTEN_PORT = int(os.environ.get("LISTEN_PORT", 11111))
WEBAPP_PORT = int(os.environ.get("WEBAPP_PORT", 3000))
ONWARD_HOME = os.environ["ONWARD_HOME"]
WEBAPP_CONTAINER_NAME = "onward-webapp-dev-{}".format(WEBAPP_PORT)

routes = web.RouteTableDef()

q = asyncio.Queue()


async def bg_handle_loop() -> None:
    # everything gets executed in serial this way
    logging.info("bg handle loop started")
    while True:
        work = await q.get()
        try:
            await work()
        except asyncio.CancelledError:
            logging.error("bg handle cancelled")
            return
        except Exception as e:
            logging.exception("bg handle exception: %s", e)
    return


def get_webapp_image_name(rev: str) -> str:
    return "tengelisconsulting/onward_webapp:dev-{}".format(rev)


def get_env(rev: str) -> Dict:
    return {"COMMON_VSN": rev}


async def update_dev_webapp_image(rev: str) -> None:
    logging.info("updating dev webapp image to %s", rev)
    res = subprocess.run(["docker", "pull", get_webapp_image_name(rev)])
    res.check_returncode()
    res = subprocess.run(["docker", "stop", WEBAPP_CONTAINER_NAME])
    if res.returncode != 0:
        logging.error("failed to stop existing webapp container")
    res = subprocess.run([
        "docker", "run", "-d", "--net=host", "--rm",
        "-e", "PORT={}".format(WEBAPP_PORT),
        "--name", WEBAPP_CONTAINER_NAME,
        get_webapp_image_name(rev)
    ])
    res.check_returncode()
    return


def run_with_env(
        cmd: str,
        env=None,
        die_on_err: bool = True
) -> None:
    res = subprocess.run(
        ["bash", "-c", "source ./env/prod.env && {}".format(cmd)],
        env=env,
        cwd=ONWARD_HOME
    )
    if res.returncode != 0:
        logging.error("cmd failed: %s", cmd)
        res.check_returncode()
    return


def parse_image_line(line: str) -> Dict:
    line_parts = line.split()
    return {
        "name": line_parts[0],
        "tag": line_parts[1],
        "hash": line_parts[2],
    }


def cleanup_backend_images(cur_rev: str) -> None:
    logging.info("cleaning up images")

    def ensure_onward(image: Dict) -> bool:
        return re.match("onwardapp/.+", image["name"])

    def is_cur_rev(image: Dict) -> bool:
        return image["tag"] == cur_rev
    res = subprocess.run(["bash", "-c", "echo 'y' | docker system prune"])
    output_lines = (
        subprocess.check_output(
            ["bash", "-c", "docker images | grep onwardapp"])
        .decode("utf-8")
        .split("\n"))
    images = [parse_image_line(line) for line in output_lines if line]
    to_delete = [image for image in images
                 if (ensure_onward(image)
                     and not is_cur_rev(image))]
    for image in to_delete:
        res = subprocess.run(
            ["docker", "rmi", image["hash"]]
        )
        if res.returncode != 0:
            logging.error("couldn't delete image %s", image)
    return


def cleanup_webapp_images(rev: str) -> None:
    images = [
        parse_image_line(line)
        for line in subprocess.check_output([
            "bash", "-c", "docker images | grep onward_webapp"
        ]).decode("utf-8").split("\n")
        if line
    ]
    current_image_name = get_webapp_image_name(rev)
    for image in images:
        if current_image_name != "{}:{}".format(image["name"], image["tag"]):
            subprocess.run(["docker", "rmi", image["hash"]])
    return


async def update_backend_containers_and_db(rev: str) -> None:
    logging.info("updating backend services and db")
    env = get_env(rev)
    run_with_env("docker-compose pull", env=env)
    run_with_env("docker-compose down --remove-orphans", env=env)
    run_with_env("./db/bin/upgrade.sh")
    run_with_env("docker-compose up -d", env=env)
    return


async def update_repo(rev: str) -> None:
    logging.info("updating repository")
    run_with_env("git pull", env=get_env(rev))
    return


@routes.post("/onward/build-success/webapp/{rev}")
async def build_success_webapp(req):
    async def work():
        await update_dev_webapp_image(rev)
        cleanup_webapp_images(rev)
        return
    rev = req.match_info["rev"]
    logging.info("webapp build success for revision: %s", rev)
    q.put_nowait(work)
    return web.Response(text="OK")


@routes.post("/onward/build-success/backend/{rev}")
async def build_success_backend(req):
    async def work():
        await update_repo(rev)
        await update_backend_containers_and_db(rev)
        cleanup_backend_images(rev)
        return
    rev = req.match_info["rev"]
    logging.info("backend build success for revision: %s", rev)
    q.put_nowait(work)
    return web.Response(text="OK")


def main():
    logging.basicConfig(level="INFO")
    loop = asyncio.get_event_loop()
    loop.create_task(bg_handle_loop())
    app = web.Application()
    app.add_routes(routes)
    logging.info("listening on %s", LISTEN_PORT)
    web.run_app(app, port=LISTEN_PORT)
    return


if __name__ == '__main__':
    main()

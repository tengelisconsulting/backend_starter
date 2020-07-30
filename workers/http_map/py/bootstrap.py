import json

from app import app
import ez


@ez.endpoint(route=b"/encode-json")
async def encode_json(
        as_text: str
):
    as_json = json.loads(as_text)
    return (b"OK", {"json": as_json})


@ez.endpoint(route=b"/test-empty")
async def test_empty():
    return (b"OK", "OK!")


async def init() -> None:
    app.ez = await ez.new_requester()
    return


async def close() -> None:
    await app.ez.client.close()
    return

from app import app
import ez


async def init() -> None:
    app.ez = await ez.new_requester()
    return


async def close() -> None:
    await app.ez.client.close()
    return

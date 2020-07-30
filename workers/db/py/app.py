from types import SimpleNamespace

import asyncpg.pool


class App(SimpleNamespace):
    db_pool: asyncpg.pool.Pool


app = App()

import os
from typing import NamedTuple


class _ENV(NamedTuple):
    PGDB: str = os.environ.get("PGDB", "postgres")
    PGHOST: str = os.environ["PGHOST"]
    PGUSER: str = os.environ.get("PGUSER", "postgres")
    PGPASSWORD: str = os.environ["PGPASSWORD"]


ENV = _ENV()

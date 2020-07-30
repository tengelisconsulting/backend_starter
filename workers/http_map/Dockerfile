FROM tengelisconsulting/ez_worker_mypy
WORKDIR /app
COPY ./py ./py
RUN mypy --ignore-missing-imports ./py

FROM tengelisconsulting/ez_worker_base
WORKDIR /app
COPY ./py ./py
ENTRYPOINT [ "tini", "/app/py/main.py" ]

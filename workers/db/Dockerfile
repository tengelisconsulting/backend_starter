FROM tengelisconsulting/ez_worker_mypy
WORKDIR /app
COPY ./py ./py
RUN mypy --ignore-missing-imports ./py

FROM tengelisconsulting/ez_worker_base
WORKDIR /app
RUN apk add --update --no-cache \
        build-base \
        python3-dev \
        && python3 -m pip install \
        asyncpg==0.20.1 \
        && apk del \
        build-base \
        python3-dev
COPY ./py ./py
ENTRYPOINT [ "tini", "/app/py/main.py" ]

FROM tengelisconsulting/pyzmq:alpine
RUN apk add --update --no-cache \
        postgresql-client \
        build-base \
        bash \
        python3-dev \
        libffi-dev \
        openssl-dev \
        && python3 -m pip install \
        asyncpg==0.20.1 \
        requests \
        cryptography==2.9.2 \
        pytz==2020.1 \
        google-auth-oauthlib==0.4.1 \
        google-api-python-client==1.8.4 \
        && apk del \
        build-base \
        python3-dev

COPY ./workers/ez_arch_worker ./ez_arch_worker
RUN python3 -m pip install --upgrade ./ez_arch_worker

WORKDIR /app
COPY ./db ./db
COPY ./tests ./tests

ENTRYPOINT [ "/app/tests/test.py" ]

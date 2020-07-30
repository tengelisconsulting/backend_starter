FROM python:3.8-alpine
RUN apk add --update --no-cache \
        bash \
        postgresql-client

WORKDIR /app
COPY ./schema ./schema
COPY ./migrate ./migrate
COPY ./bin ./bin

ARG GIT_REV="NONE"
ENV GIT_REV=$GIT_REV
ENTRYPOINT [ "/app/bin/install.sh" ]

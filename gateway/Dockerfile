FROM tengelisconsulting/gateway_base:5c19a92

VOLUME /app/logs

COPY ./entrypoint.sh ./entrypoint.sh

COPY ./ez_client.lua ./ez_client.lua

COPY ./nginx ./nginx
COPY ./lua ./lua

ARG GIT_REV="NONE"
ENV GIT_REV=$GIT_REV

ENTRYPOINT [ "/tini", "/app/entrypoint.sh" ]

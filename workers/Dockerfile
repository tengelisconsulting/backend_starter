FROM tengelisconsulting/pyzmq:alpine
WORKDIR /app/py
COPY ./ez_arch_worker ./ez_arch_worker
RUN python3 -m pip install \
        ./ez_arch_worker
COPY ./ez.py ./ez.py
COPY ./ez_worker_main.py ./main.py

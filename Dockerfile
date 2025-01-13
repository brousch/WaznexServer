FROM ubuntu:24.04
# 24.04 provides python 3.12

ENV DEBIAN_FRONTEND=noninteractive

ENV BASE=/opt/waznexserver
ENV CODE=$BASE/WaznexServer
ENV VENV=$BASE/env
ENV PIP=$VENV/bin/pip
ENV PYTHON=$VENV/bin/python

RUN mkdir $BASE

RUN apt-get update && apt-get install -y  \
    run-one \
    python3 \
    python3-venv \
    python-is-python3  \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv $VENV
RUN $PIP install --upgrade pip

WORKDIR $CODE

COPY ./requirements.txt $CODE/
RUN $PIP install -r requirements.txt

COPY . $CODE

ENV PATH=$VENV/bin:$PATH

RUN $PYTHON -m waznexserver.init_data

EXPOSE 8080

# using array for CMD avoids shell intermediary, so that Ctrl-C works
CMD [ \
    "gunicorn", \
    "--workers", "2", \
    "--threads", "4", \
    "--worker-tmp-dir", "/dev/shm", \
    # for nginx:
    "--bind", "unix:waznexserver.sock", \
    # for direct access:
    "--bind", ":8080", \
    "--umask", "007", \
#    "--access-logfile", "-", \
    "--capture-output", \
    "waznexserver.waznexserver:create_app()" \
]

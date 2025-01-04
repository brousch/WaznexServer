# Bionic
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

ENV BASE=/opt/waznexserver
ENV CODE=$BASE/WaznexServer
ENV VENV=$BASE/env
ENV PIP=$VENV/bin/pip
ENV PYTHON=$VENV/bin/python

RUN mkdir $BASE

RUN apt-get update
RUN apt-get install -y nginx python-dev libjpeg62 libjpeg-dev libfreetype6 libfreetype6-dev libtiff5 libtiff5-dev libwebp6 libwebp-dev zlib1g-dev run-one
RUN apt-get install -y curl  \
    && curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python  \
    && pip --version
RUN pip install -U pip
RUN python -m pip install -U virtualenv
RUN virtualenv -p python2.7 $VENV

WORKDIR $CODE

COPY ./requirements.txt $CODE/
RUN $PIP install -r requirements.txt

COPY . $CODE

ENV PATH=$VENV/bin:$PATH

RUN waznexserver/init_data.py

EXPOSE 8080

# using array for CMD avoids shell intermediary, so that Ctrl-C works
RUN chmod +x waznexserver/waznexserver.py
CMD ["waznexserver/waznexserver.py"]

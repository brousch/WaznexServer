#!/usr/bin/env bash

NUM_WORKERS=8
SERVER_PORT=127.0.0.1:8000
cd /opt/waznexserver/WaznexServer/
exec /opt/waznexserver/env/bin/gunicorn -w $NUM_WORKERS -b $SERVER_PORT waznexserver.waznexserver:app

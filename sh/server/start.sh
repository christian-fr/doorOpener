#!/bin/bash

source /etc/doorOpener/.env_server
pwd
export FLASK_APP=app
export SERVICE_PORT=5050
echo "$SERVICE_PORT"
# flask run
python3 -m "app.app"

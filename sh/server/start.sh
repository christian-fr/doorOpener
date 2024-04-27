#!/bin/bash
FLASK_APP=app
set -a
source /etc/doorOpener/.env_server
set +a
python3 -m "app.app"

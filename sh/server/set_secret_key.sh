#!/bin/bash
sed -i "s/SECRET_KEY=.*$/SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')/" /etc/doorOpener/.env_server

#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

SECRET_KEY=$(python3 -c "import json; print(json.load(open('${CONFIG_PATH}')).get('secret_key', ''))")
if [ -n "${SECRET_KEY}" ]; then
    export MANARA_SECRET_KEY="${SECRET_KEY}"
fi

LOG_LEVEL=$(python3 -c "import json; print(json.load(open('${CONFIG_PATH}')).get('log_level', 'info'))")

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level "${LOG_LEVEL}"

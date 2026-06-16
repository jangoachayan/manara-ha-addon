#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

SECRET_KEY=$(python3 -c "import json; print(json.load(open('${CONFIG_PATH}')).get('secret_key', ''))")
if [ -n "${SECRET_KEY}" ]; then
    export MANARA_SECRET_KEY="${SECRET_KEY}"
fi

LOG_LEVEL=$(python3 -c "import json; print(json.load(open('${CONFIG_PATH}')).get('log_level', 'info'))")

# Start cloudflared quick tunnel in the background
cloudflared tunnel --url http://localhost:8000 --no-autoupdate > /tmp/cloudflared.log 2>&1 &

# Wait for the tunnel to establish and print its URL
sleep 8
MANARA_TUNNEL_URL=$(grep -o 'https://[a-zA-Z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log | head -1 || true)
export MANARA_TUNNEL_URL
echo "Manara tunnel URL: ${MANARA_TUNNEL_URL}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level "${LOG_LEVEL}"

#!/usr/bin/env bash
set -euo pipefail

# ensure /data exists
mkdir -p /data

# append a UTC timestamp as heartbeat
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') cron heartbeat" >> /data/cron_heartbeat.log

# optional: hit the local API health endpoint and log failures
if ! curl -sS --max-time 5 http://127.0.0.1:8080/generate-2fa >/dev/null; then
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') api-check FAILED" >> /data/cron_errors.log
fi

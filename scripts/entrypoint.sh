#!/bin/sh
set -e

# Extract PORT from Render/Railway/Cloud environment, fallback to 8000
if [ -z "$PORT" ]; then
  PORT=8000
fi

echo "=========================================================="
echo "🚀 Launching LoanAI Decision Platform on Port $PORT"
echo "=========================================================="

exec uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

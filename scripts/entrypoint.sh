#!/bin/sh
set -e

# Resolve port from Railway/cloud environment variable, fallback to 8000
PORT="${PORT:-8000}"

echo "=========================================================="
echo "🚀 Launching LoanAI Decision Platform on Port $PORT"
echo "=========================================================="

exec uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

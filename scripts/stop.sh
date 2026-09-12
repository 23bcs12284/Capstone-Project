#!/bin/bash
# ==============================================================================
# Stop Script - Cleanly terminates LoanAI Decision Platform servers
# ==============================================================================

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PORT=8000
if [ -f .env ]; then
    PORT_IN_ENV=$(grep -E '^PORT=' .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$PORT_IN_ENV" ]; then
        PORT=$PORT_IN_ENV
    fi
fi

echo "🛑 Stopping LoanAI server on port ${PORT}..."

# Kill process listening on target port
PIDS=$(lsof -ti:${PORT} 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "Killing process on port ${PORT} (PID: ${PIDS})..."
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    echo "✓ Port ${PORT} released."
else
    echo "✓ No process found on port ${PORT}."
fi

# Kill any remaining uvicorn instances for backend.main:app
UVICORN_PIDS=$(ps aux | grep "[u]vicorn backend.main:app" | awk '{print $2}')
if [ -n "$UVICORN_PIDS" ]; then
    echo "Cleaning up lingering Uvicorn workers (PIDs: ${UVICORN_PIDS})..."
    echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null || true
fi

echo "✨ Server stopped successfully."

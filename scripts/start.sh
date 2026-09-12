#!/bin/bash
# ==============================================================================
# Production-Ready Single Command Application Launcher
# ==============================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load virtual environment if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ensure .env exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
fi

# Parse Mode (--prod or --dev)
MODE="dev"
for arg in "$@"; do
    if [ "$arg" == "--prod" ]; then
        MODE="prod"
    elif [ "$arg" == "--dev" ]; then
        MODE="dev"
    fi
done

PORT=8000
HOST="0.0.0.0"

if [ -f .env ]; then
    PORT_VAL=$(grep -E '^PORT=' .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    HOST_VAL=$(grep -E '^HOST=' .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$PORT_VAL" ]; then PORT=$PORT_VAL; fi
    if [ -n "$HOST_VAL" ]; then HOST=$HOST_VAL; fi
fi

echo "=========================================================="
echo "🚀 Launching LoanAI Decision Platform (${MODE} mode)"
echo "=========================================================="

# Resolve Port Conflicts automatically
PIDS=$(lsof -ti:${PORT} 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "⚠️ Port ${PORT} occupied by PID(s): ${PIDS}. Cleaning up..."
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✓ Port ${PORT} cleared."
fi

if [ "$MODE" == "prod" ]; then
    export ENVIRONMENT="production"
    export RELOAD="false"
    echo "🌐 Environment: PRODUCTION (No auto-reload)"
    echo "📍 Server: http://${HOST}:${PORT}"
    exec python3 -m backend.main
else
    export ENVIRONMENT="development"
    export RELOAD="true"
    echo "🛠️ Environment: DEVELOPMENT (Auto-reload scoped to backend/ & config/)"
    echo "📍 Server: http://${HOST}:${PORT}"
    exec python3 -m backend.main
fi

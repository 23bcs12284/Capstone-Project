#!/bin/bash
# ==============================================================================
# Primary Entry Point - LoanAI Decision Support System
# ==============================================================================
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$PROJECT_ROOT/scripts/start.sh" "$@"

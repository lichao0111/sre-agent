#!/usr/bin/env bash
set -euo pipefail
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
uvicorn sre_agent.app.main:app --reload --port 8000

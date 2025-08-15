#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate || true
# Start backend
(uvicorn backend.app:app --reload --port 8000 &) 
# Start frontend
cd frontend && npm run dev

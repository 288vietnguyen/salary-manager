#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Salary Manager ==="

# Create virtual environment if it doesn't exist
if [ ! -d "$ROOT/venv" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv "$ROOT/venv"
fi

# Install / update dependencies
echo "[2/3] Installing dependencies..."
"$ROOT/venv/bin/pip" install --quiet --upgrade pip
"$ROOT/venv/bin/pip" install --quiet -r "$ROOT/requirements.txt"

# Create models directory if missing
mkdir -p "$ROOT/backend/models"

# Start server
echo "[3/3] Starting server at http://localhost:8080"
cd "$ROOT/backend"
"$ROOT/venv/bin/python" -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload

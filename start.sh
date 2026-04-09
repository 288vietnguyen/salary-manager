#!/bin/bash
cd "$(dirname "$0")"
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting Salary Manager on http://localhost:8000"
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload

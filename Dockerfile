FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# SQLite DB lives in backend/ — mount a volume there to persist data
VOLUME ["/app/backend"]

EXPOSE 8080

# Run from /app/backend so relative imports (database, ../frontend) resolve correctly
WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

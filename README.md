# Salary Manager

A personal salary tracking app with monthly income recording, analytics, and multi-language support (English / Vietnamese).

---

## Features

- Record monthly income with notes
- Income history table
- Analytics: Monthly vs base salary, Quarterly summary, Annual summary
- Light / Dark theme
- English / Vietnamese language toggle

---

## Running Locally

### Prerequisites

| OS | Requirement |
|----|-------------|
| Windows | Python 3.10+ from [python.org](https://www.python.org/downloads/) |
| macOS | Python 3.10+ via `brew install python` or [python.org](https://www.python.org/downloads/) |
| Linux | `sudo apt install python3 python3-pip` (Debian/Ubuntu) or equivalent |

### Windows

```bat
start.bat
```

Or manually:

```bat
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

### macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

Or manually:

```bash
pip3 install -r requirements.txt
cd backend
python3 -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

### Open the app

Visit [http://localhost:8080](http://localhost:8080) in your browser.

> The SQLite database (`salary_manager.db`) is created automatically inside the `backend/` folder on first run.

---

## Running with Docker

### Prerequisites

Install Docker Desktop:
- **Windows / macOS**: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

### Build the image

```bash
docker build -t salary-manager .
```

### Run the container

```bash
docker run -p 8080:8080 -v salary-manager-data:/app/backend salary-manager
```

This mounts a named volume (`salary-manager-data`) so your data persists across container restarts.

### Open the app

Visit [http://localhost:8080](http://localhost:8080) in your browser.

### Stop the container

```bash
docker ps                        # find the container ID
docker stop <container-id>
```

### Remove data volume (reset all data)

```bash
docker volume rm salary-manager-data
```

---

## Project Structure

```
salary-manager/
├── backend/
│   ├── main.py          # FastAPI app & API routes
│   └── database.py      # SQLite setup & queries
├── frontend/
│   ├── index.html       # Single-page UI
│   ├── app.js           # All frontend logic & i18n
│   └── style.css        # Styles (dark/light theme)
├── requirements.txt
├── Dockerfile
├── start.bat            # Windows launcher
└── start.sh             # macOS / Linux launcher
```

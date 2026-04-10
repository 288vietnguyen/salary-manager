# Salary Manager

A personal salary tracking app with monthly income recording, analytics, Gmail import, and multi-language support (English / Vietnamese).

---

## Features

- Record monthly income with notes
- Delete individual income records
- Analytics: Monthly vs base salary, Quarterly summary, Annual summary
- **Gmail Import** — scan payslip emails and auto-extract income amounts
  - Supports plain text, HTML table, and image (OCR) payslip formats
- Light / Dark theme
- English / Vietnamese language toggle

---

## Prerequisites

| | Windows | macOS | Linux |
|---|---|---|---|
| **Python** | 3.10+ from [python.org](https://www.python.org/downloads/) | `brew install python` or [python.org](https://www.python.org/downloads/) | `sudo apt install python3 python3-pip python3-venv` |
| **Git** | [git-scm.com](https://git-scm.com/download/win) | `brew install git` | `sudo apt install git` |
| **Build .exe (Windows only)** | Included in `build_exe.bat` | — | — |

> macOS / Linux build produces a native binary via the same PyInstaller spec — use `build_exe.sh`.

---

## Running Locally

### 1. Clone the repository

```bash
git clone <repo-url>
cd salary-manager
```

### 2. Start the server

**Windows** — double-click or run in terminal:
```bat
start.bat
```

**macOS / Linux**:
```bash
chmod +x start.sh
./start.sh
```

Both scripts automatically:
- Create a Python virtual environment (`venv/`) on first run
- Install all dependencies from `requirements.txt`
- Start the server at `http://localhost:8080`

### 3. Open the app

Visit [http://localhost:8080](http://localhost:8080) in your browser.

> The SQLite database (`backend/salary_manager.db`) is created automatically on first run.

---

## Building a Standalone Executable

The build scripts use **PyInstaller** to bundle the app into a single folder with no Python installation required.

### Windows → `.exe`

```bat
build\build_exe.bat
```

What the script does:
1. Checks Python is installed
2. Installs `requirements.txt` + `pyinstaller`
3. Downloads EasyOCR models (`craft_mlt_25k.pth`, `latin_g2.pth`) into `backend/models/`
4. Runs PyInstaller with `build/salary-manager.spec`

Output: `dist\SalaryManager\SalaryManager.exe`

To distribute: copy the entire `dist\SalaryManager\` folder.

### macOS / Linux → native binary

```bash
chmod +x build/build_exe.sh
bash build/build_exe.sh
```

Output: `dist/SalaryManager/SalaryManager`

To run the built binary:
```bash
./dist/SalaryManager/SalaryManager
```

> On macOS you may need to allow the app in **System Preferences → Security & Privacy** on first launch.

### Notes on the build

- The app opens automatically in your default browser when launched
- Logs are written to `salary-manager.log` next to the executable (useful for debugging)
- The SQLite database is stored next to the executable and persists between runs
- OCR models (~67 MB) are bundled by the build script — no internet required after build

---

## Running with Docker

### Prerequisites

- **Windows / macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

### Build the image

```bash
docker build -t salary-manager .
```

### Run the container

**macOS / Linux:**
```bash
docker run -p 8080:8080 \
  -v "$(pwd)/backend/salary_manager.db:/app/backend/salary_manager.db" \
  -v "$(pwd)/backend/gmail_config.json:/app/backend/gmail_config.json" \
  -v "$(pwd)/backend/models:/app/backend/models" \
  salary-manager
```

**Windows (Command Prompt):**
```bat
docker run -p 8080:8080 ^
  -v "%cd%\backend\salary_manager.db:/app/backend/salary_manager.db" ^
  -v "%cd%\backend\gmail_config.json:/app/backend/gmail_config.json" ^
  -v "%cd%\backend\models:/app/backend/models" ^
  salary-manager
```

**Windows (PowerShell):**
```powershell
docker run -p 8080:8080 `
  -v "${PWD}\backend\salary_manager.db:/app/backend/salary_manager.db" `
  -v "${PWD}\backend\gmail_config.json:/app/backend/gmail_config.json" `
  -v "${PWD}\backend\models:/app/backend/models" `
  salary-manager
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

### Stop the container

```bash
docker ps                   # find the CONTAINER ID
docker stop <container-id>
```

---

## Gmail Import Setup

The Gmail Import feature connects via **IMAP** — no Google Cloud Console or OAuth required.

### Step 1 — Enable IMAP in Gmail

1. Open Gmail → **Settings** (gear icon) → **See all settings**
2. Go to **Forwarding and POP/IMAP** tab
3. Under **IMAP access**, select **Enable IMAP** → **Save Changes**

### Step 2 — Generate an App Password

> Requires **2-Step Verification** to be enabled on your Google Account.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Enter a name (e.g. `Salary Manager`) and click **Create**
3. Copy the 16-character password shown

### Step 3 — Configure in the app

1. Open the app → click **Settings** in the Gmail Import card
2. Enter your Gmail address and the App Password
3. Enter the **Sender Email / Domain** of your payslip emails (e.g. `payroll@company.com`)
4. Optionally enter an **Amount Regex** with a named group `amount`, e.g:
   ```
   Total:\s+(?P<amount>[\d,]+)
   ```
5. Click **Save**

### Step 4 — Scan and import

1. Click **Scan Emails** — detected entries appear in a preview table
2. Check the entries to import → click **Import Selected**

---

## Project Structure

```
salary-manager/
├── backend/
│   ├── main.py                # FastAPI app & API routes
│   ├── database.py            # SQLite setup & queries
│   ├── gmail_integration.py   # Gmail IMAP + OCR extraction
│   ├── gmail_config.json      # Gmail credentials (auto-created, gitignored)
│   └── models/                # EasyOCR model files (optional, for image payslips)
├── build/
│   ├── salary-manager.spec    # PyInstaller spec
│   ├── build_exe.bat          # Windows build script
│   └── build_exe.sh           # macOS / Linux build script
├── frontend/
│   ├── index.html             # Single-page UI
│   ├── app.js                 # Frontend logic & i18n
│   └── style.css              # Styles (dark/light theme)
├── requirements.txt
├── Dockerfile
├── start.bat                  # Windows: run locally
└── start.sh                   # macOS / Linux: run locally
```

---

## Security Notes

- `backend/gmail_config.json` stores your Gmail App Password in plain text — keep it local and never commit it
- It is listed in `.gitignore` by default

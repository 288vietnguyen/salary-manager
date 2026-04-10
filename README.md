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

### macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

Both scripts automatically create a virtual environment, install dependencies, and start the server.

### Open the app

Visit [http://localhost:8080](http://localhost:8080) in your browser.

> The SQLite database (`salary_manager.db`) is created automatically inside `backend/` on first run.

---

## Gmail Import Setup

The Gmail Import feature connects directly to Gmail via **IMAP** — no Google Cloud Console or OAuth required.

### Step 1 — Enable IMAP in Gmail

1. Open Gmail → **Settings** (gear icon) → **See all settings**
2. Go to **Forwarding and POP/IMAP** tab
3. Under **IMAP access**, select **Enable IMAP**
4. Click **Save Changes**

### Step 2 — Generate an App Password

> App Passwords require **2-Step Verification** to be enabled on your Google Account.

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Enter a name (e.g. `Salary Manager`) and click **Create**
3. Copy the 16-character password shown

### Step 3 — Configure in the app

1. Open the app → click **Settings** in the Gmail Import card
2. Enter your Gmail address and the App Password from Step 2
3. Enter the **Sender Email / Domain** of your payslip emails (e.g. `payroll@company.com`)
4. Optionally enter an **Amount Regex** if your emails contain text amounts.
   Use a named capture group called `amount`, e.g:
   ```
   Total:\s+(?P<amount>[\d,]+)
   ```
   Leave blank to rely on keyword detection (`Lương net`, `Thực nhận`, etc.)
5. Click **Save** — the status badge will turn **Connected**

### Step 4 — Scan emails

1. Click **Scan Emails** — a loading screen appears while emails are fetched
2. A preview table shows detected entries with year, month, and extracted amount
3. Check the entries you want to import and click **Import Selected**

> Entries where no amount could be extracted are shown dimmed and cannot be selected.

### How amount extraction works

The app tries three methods in order:

| Method | Used when |
|--------|-----------|
| **Regex on plain text** | Email has a text body and you configured a regex |
| **Keyword search on HTML table** | Email body is an HTML table (e.g. Vietnamese payslip format) — looks for rows containing `Lương net`, `Thực nhận`, etc. |
| **OCR on image attachment** | Payslip is sent as an image — uses EasyOCR with local models |

> OCR models (~67 MB total) are downloaded automatically to `backend/models/` on first use.

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
docker run -p 8080:8080 \
  -v "$(pwd)/backend/salary_manager.db:/app/backend/salary_manager.db" \
  -v "$(pwd)/backend/gmail_config.json:/app/backend/gmail_config.json" \
  -v "$(pwd)/backend/models:/app/backend/models" \
  salary-manager
```

Bind-mounting individual files and the models folder keeps your data on the host while the source code stays inside the image. On Windows use `%cd%` instead of `$(pwd)`.

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
│   ├── main.py               # FastAPI app & API routes
│   ├── database.py           # SQLite setup & queries
│   ├── gmail_integration.py  # Gmail IMAP + OCR logic
│   ├── gmail_config.json     # Gmail credentials (auto-created, gitignored)
│   └── models/               # EasyOCR model files (optional, for image payslips)
├── frontend/
│   ├── index.html            # Single-page UI
│   ├── app.js                # All frontend logic & i18n
│   └── style.css             # Styles (dark/light theme)
├── requirements.txt
├── Dockerfile
├── start.bat                 # Windows launcher
└── start.sh                  # macOS / Linux launcher
```

---

## Security Notes

- `backend/gmail_config.json` stores your Gmail App Password in plain text — keep it local and never commit it to version control.
- Add it to `.gitignore`:
  ```
  backend/gmail_config.json
  backend/gmail_config_example.json
  ```

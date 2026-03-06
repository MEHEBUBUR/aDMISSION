# PM SHRI Kendriya Vidyalaya Barpeta - Class XI Admission Portal (2026-27)

A full-stack online admission system built with Flask, SQLite, Bootstrap, HTML/CSS/JavaScript aligned to KVS admission workflow.

## Folder Structure

```
aDMISSION/
├── app.py
├── requirements.txt
├── admission.db (auto-created)
├── app/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── apply.html
│   │   ├── success.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── interview_list.html
│   │   ├── merit_list.html
│   │   └── _merit_table.html
│   └── uploads/
└── docs/
    └── schema.sql
```

## Features

- Home page with school branding, logo, announcement and apply CTA.
- End-to-end online Class XI application form:
  - Student, parent, academic details
  - Subject-wise marks entry with automatic total and percentage
  - Stream selection with KVS eligibility hints
  - Document upload (marksheet, TC, Aadhaar, photo, caste certificate)
- KVS-like stream eligibility checks:
  - Science: >=60% aggregate and >=60 in Maths + Science
  - Commerce: >=55% aggregate
  - Humanities: all pass students
- Merit score calculation (out of 100):
  - Class X percentage weight: 80
  - Service category priority: 10
  - Sports/NCC: 10
- Automatic shortlist status:
  - >=70: Shortlisted for Interview
  - 50-69: Waiting List
  - <50: Not Selected
- Admin panel with login, application review, approval/rejection, interview scheduling.
- Interview list page + PDF download.
- Merit list generation (selected, waiting, rejected) with tie-break ordering:
  1. Higher Maths
  2. Higher Maths + Science
  3. Older candidate (DOB)
- CSV export for application data.

## Setup & Run

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the Flask app:

```bash
python app.py
```

3. Open:

- Home: `http://127.0.0.1:5000/`
- Apply: `http://127.0.0.1:5000/apply`
- Admin Login: `http://127.0.0.1:5000/admin/login`

## HOW TO USE THIS IN VS CODE

1. Open VS Code.
2. Go to **File > Open Folder...** and select the `aDMISSION` project folder.
3. Open the terminal in VS Code (**Terminal > New Terminal**).
4. Create and activate virtual environment:

### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Start server:

```bash
python app.py
```

7. In VS Code terminal, Ctrl+Click this URL: `http://127.0.0.1:5000/`.

### VS Code Extensions (recommended)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- SQLite Viewer (optional for inspecting `admission.db`)

## Admin Credentials (default)

- Username: `admin`
- Password: `admin123`

> Change credentials and secret key before production deployment.

## Database

SQLite database (`admission.db`) initializes automatically on first run.
Schema reference: `docs/schema.sql`.

## Troubleshooting

- If `ModuleNotFoundError: No module named 'flask'` appears, ensure the virtual environment is activated and run `pip install -r requirements.txt` again.
- If dependency install fails in restricted networks, configure `pip` proxy/index settings per your environment policy.


## Deploy on Render

If your Render logs show:

- `error: could not find Cargo.toml in /opt/render/project/src`

it means the service is currently configured as Rust (`cargo build --release`).

Use these exact settings for this Python Flask app:

- **Environment**: `Python 3`
- **Build Command**: `bash ./scripts/render-build.sh`
- Flask is installed explicitly inside this script.
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Important for existing Render services

If the service was created earlier with Rust defaults, updating files alone is not enough. In Render dashboard:

1. Open your Web Service **Settings**.
2. Replace Build/Start commands with the values above.
3. Click **Save Changes**.
4. Run **Manual Deploy -> Clear build cache & deploy**.

### Files included for Render

- `render.yaml` (Blueprint config for new services)
- `Procfile` (process declaration)
- `scripts/render-build.sh` (deterministic Python dependency install)

After these changes, Render will stop trying to run `cargo`.


### Cargo build fallback compatibility

Some Render services are accidentally created with Rust defaults and run `cargo build --release`
before app settings are corrected. To prevent immediate build failure (`could not find Cargo.toml`),
this repo includes a minimal Rust shim (`Cargo.toml` + `src/main.rs`) so the build step can complete.

> The real runtime remains Python Flask via: `gunicorn app:app --bind 0.0.0.0:$PORT`.


## Render Blueprint Deploy (Recommended)

1. Push this repository to GitHub.
2. In Render, click **New +** -> **Blueprint**.
3. Select this repository. Render reads `render.yaml` automatically.
4. Confirm service settings:
   - Build command: `bash ./scripts/render-build.sh`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Deploy.
6. Verify health check: `/health`

If your old service still shows `cargo build --release`, either:
- update that service settings manually, or
- create a **new Blueprint service** from this repository.

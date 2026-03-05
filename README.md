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

If Render auto-detected this repository as Rust and shows:

- Build Command: `cargo build --release`

change it to Python settings:

- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

This repository now includes both:

- `render.yaml` (Blueprint config)
- `Procfile` (process declaration)

So Render can deploy without `cargo`.

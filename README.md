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

## Admin Credentials (default)

- Username: `admin`
- Password: `admin123`

> Change credentials and secret key before production deployment.

## Database

SQLite database (`admission.db`) initializes automatically on first run.
Schema reference: `docs/schema.sql`.

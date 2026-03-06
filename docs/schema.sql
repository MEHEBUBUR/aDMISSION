CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    gender TEXT NOT NULL,
    aadhaar_number TEXT NOT NULL,
    religion TEXT,
    category TEXT NOT NULL,
    father_name TEXT NOT NULL,
    mother_name TEXT NOT NULL,
    occupation TEXT,
    service_category TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    board_name TEXT NOT NULL,
    previous_school TEXT NOT NULL,
    class_x_roll_number TEXT NOT NULL,
    year_of_passing INTEGER NOT NULL,
    stream_selected TEXT NOT NULL,
    sports_ncc INTEGER DEFAULT 0,
    eligibility_status TEXT NOT NULL,
    application_status TEXT DEFAULT 'Submitted',
    created_at TEXT NOT NULL
);

CREATE TABLE marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    english REAL NOT NULL,
    mathematics REAL NOT NULL,
    science REAL NOT NULL,
    social_science REAL NOT NULL,
    optional_subject REAL NOT NULL,
    total_marks REAL NOT NULL,
    percentage REAL NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    marksheet_path TEXT NOT NULL,
    tc_path TEXT NOT NULL,
    aadhaar_path TEXT NOT NULL,
    photo_path TEXT NOT NULL,
    caste_certificate_path TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
);

CREATE TABLE merit_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    percentage_component REAL NOT NULL,
    service_component REAL NOT NULL,
    sports_component REAL NOT NULL,
    merit_score REAL NOT NULL,
    shortlist_status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
);

CREATE TABLE interview_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    interview_date TEXT,
    interview_time TEXT,
    remarks TEXT,
    final_status TEXT DEFAULT 'Pending',
    FOREIGN KEY(student_id) REFERENCES students(id)
);

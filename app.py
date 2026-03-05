import csv
import io
import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:
    canvas = None
    A4 = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "admission.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-in-production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
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

        CREATE TABLE IF NOT EXISTS marks (
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

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            marksheet_path TEXT NOT NULL,
            tc_path TEXT NOT NULL,
            aadhaar_path TEXT NOT NULL,
            photo_path TEXT NOT NULL,
            caste_certificate_path TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS merit_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            percentage_component REAL NOT NULL,
            service_component REAL NOT NULL,
            sports_component REAL NOT NULL,
            merit_score REAL NOT NULL,
            shortlist_status TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS interview_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            interview_date TEXT,
            interview_time TEXT,
            remarks TEXT,
            final_status TEXT DEFAULT 'Pending',
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """
    )
    db.commit()

    admin = db.execute("SELECT * FROM admins WHERE username=?", ("admin",)).fetchone()
    if not admin:
        db.execute(
            "INSERT INTO admins(username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        db.commit()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please login as admin.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return wrapper


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(field_name):
    file = request.files.get(field_name)
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        raise ValueError(f"Invalid file type for {field_name}")
    safe_name = secure_filename(file.filename)
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(path)
    return path


def calculate_eligibility(stream, percentage, mathematics, science):
    if stream == "Science":
        if percentage >= 60 and mathematics >= 60 and science >= 60:
            return "Eligible"
        return "Not Eligible"
    if stream == "Commerce":
        return "Eligible" if percentage >= 55 else "Not Eligible"
    return "Eligible"


def service_priority_score(service_category):
    mapping = {
        "Central Govt": 10,
        "State Govt": 8,
        "PSU": 6,
        "Private": 4,
    }
    return mapping.get(service_category, 4)


def calculate_merit(percentage, service_category, sports_ncc):
    percentage_component = round((percentage / 100) * 80, 2)
    service_component = float(service_priority_score(service_category))
    sports_component = 10.0 if sports_ncc else 0.0
    merit_score = round(percentage_component + service_component + sports_component, 2)

    if merit_score >= 70:
        shortlist_status = "Shortlisted for Interview"
    elif merit_score >= 50:
        shortlist_status = "Waiting List"
    else:
        shortlist_status = "Not Selected"

    return percentage_component, service_component, sports_component, merit_score, shortlist_status


def fetch_merit_sorted(db):
    query = """
    SELECT s.id, s.full_name, s.dob, s.stream_selected, s.application_status,
           m.percentage, m.mathematics, m.science,
           ms.merit_score, ms.shortlist_status
    FROM students s
    JOIN marks m ON m.student_id = s.id
    JOIN merit_scores ms ON ms.student_id = s.id
    ORDER BY ms.merit_score DESC,
             m.mathematics DESC,
             (m.mathematics + m.science) DESC,
             s.dob ASC
    """
    return db.execute(query).fetchall()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        try:
            english = float(request.form["english"])
            mathematics = float(request.form["mathematics"])
            science = float(request.form["science"])
            social_science = float(request.form["social_science"])
            optional_subject = float(request.form["optional_subject"])
            total_marks = english + mathematics + science + social_science + optional_subject
            percentage = round(total_marks / 5, 2)

            stream_selected = request.form["stream_selected"]
            eligibility = calculate_eligibility(stream_selected, percentage, mathematics, science)

            marksheet = save_uploaded_file("marksheet")
            tc = save_uploaded_file("transfer_certificate")
            aadhaar = save_uploaded_file("aadhaar_doc")
            photo = save_uploaded_file("photo")
            caste = save_uploaded_file("caste_certificate")

            required_docs = [marksheet, tc, aadhaar, photo]
            if any(doc is None for doc in required_docs):
                flash("Please upload all required documents.", "danger")
                return redirect(url_for("apply"))

            sports_ncc = 1 if request.form.get("sports_ncc") == "yes" else 0
            db = get_db()
            created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            cursor = db.execute(
                """
                INSERT INTO students (
                    full_name, dob, gender, aadhaar_number, religion, category,
                    father_name, mother_name, occupation, service_category,
                    mobile_number, email, address,
                    board_name, previous_school, class_x_roll_number, year_of_passing,
                    stream_selected, sports_ncc, eligibility_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.form["full_name"], request.form["dob"], request.form["gender"],
                    request.form["aadhaar_number"], request.form.get("religion", ""), request.form["category"],
                    request.form["father_name"], request.form["mother_name"], request.form.get("occupation", ""),
                    request.form["service_category"], request.form["mobile_number"], request.form["email"],
                    request.form["address"], request.form["board_name"], request.form["previous_school"],
                    request.form["class_x_roll_number"], int(request.form["year_of_passing"]),
                    stream_selected, sports_ncc, eligibility, created_at,
                ),
            )
            student_id = cursor.lastrowid

            db.execute(
                """
                INSERT INTO marks(student_id, english, mathematics, science, social_science, optional_subject, total_marks, percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (student_id, english, mathematics, science, social_science, optional_subject, total_marks, percentage),
            )
            db.execute(
                """
                INSERT INTO documents(student_id, marksheet_path, tc_path, aadhaar_path, photo_path, caste_certificate_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (student_id, marksheet, tc, aadhaar, photo, caste),
            )

            merit = calculate_merit(percentage, request.form["service_category"], sports_ncc)
            db.execute(
                """
                INSERT INTO merit_scores(student_id, percentage_component, service_component, sports_component, merit_score, shortlist_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (student_id, *merit),
            )
            db.execute("INSERT INTO interview_status(student_id) VALUES (?)", (student_id,))
            db.commit()
            flash("Application submitted successfully.", "success")
            return redirect(url_for("application_success", student_id=student_id))
        except ValueError as err:
            flash(str(err), "danger")
            return redirect(url_for("apply"))

    return render_template("apply.html")


@app.route("/success/<int:student_id>")
def application_success(student_id):
    db = get_db()
    row = db.execute(
        """
        SELECT s.full_name, s.stream_selected, s.eligibility_status, ms.merit_score, ms.shortlist_status
        FROM students s JOIN merit_scores ms ON ms.student_id=s.id
        WHERE s.id=?
        """,
        (student_id,),
    ).fetchone()
    return render_template("success.html", application=row, student_id=student_id)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    applications = db.execute(
        """
        SELECT s.*, m.percentage, ms.merit_score, ms.shortlist_status,
               i.interview_date, i.interview_time, i.final_status
        FROM students s
        JOIN marks m ON m.student_id=s.id
        JOIN merit_scores ms ON ms.student_id=s.id
        JOIN interview_status i ON i.student_id=s.id
        ORDER BY s.created_at DESC
        """
    ).fetchall()
    return render_template("admin_dashboard.html", applications=applications)


@app.route("/admin/application/<int:student_id>/status", methods=["POST"])
@login_required
def update_application_status(student_id):
    status = request.form.get("status")
    if status not in ["Approved", "Rejected", "Submitted"]:
        flash("Invalid status", "danger")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute("UPDATE students SET application_status=? WHERE id=?", (status, student_id))
    db.commit()
    flash("Application status updated", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/interview/schedule", methods=["POST"])
@login_required
def schedule_interview():
    student_id = request.form.get("student_id")
    interview_date = request.form.get("interview_date")
    interview_time = request.form.get("interview_time")
    remarks = request.form.get("remarks", "")

    db = get_db()
    db.execute(
        """
        UPDATE interview_status
        SET interview_date=?, interview_time=?, remarks=?
        WHERE student_id=?
        """,
        (interview_date, interview_time, remarks, student_id),
    )
    db.commit()
    flash("Interview scheduled", "success")
    return redirect(url_for("interview_list"))


@app.route("/admin/interview-list")
@login_required
def interview_list():
    db = get_db()
    rows = db.execute(
        """
        SELECT s.full_name, s.stream_selected, ms.merit_score,
               i.interview_date, i.interview_time, ms.shortlist_status
        FROM students s
        JOIN merit_scores ms ON ms.student_id=s.id
        JOIN interview_status i ON i.student_id=s.id
        WHERE ms.shortlist_status='Shortlisted for Interview'
        ORDER BY ms.merit_score DESC
        """
    ).fetchall()
    return render_template("interview_list.html", rows=rows)


@app.route("/admin/interview-list/pdf")
@login_required
def interview_list_pdf():
    db = get_db()
    rows = db.execute(
        """
        SELECT s.full_name, s.stream_selected, ms.merit_score,
               i.interview_date, i.interview_time
        FROM students s
        JOIN merit_scores ms ON ms.student_id=s.id
        JOIN interview_status i ON i.student_id=s.id
        WHERE ms.shortlist_status='Shortlisted for Interview'
        ORDER BY ms.merit_score DESC
        """
    ).fetchall()

    if canvas is None:
        flash("PDF export requires reportlab package.", "warning")
        return redirect(url_for("interview_list"))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "PM SHRI KV Barpeta - Class XI Interview List")
    y -= 30
    p.setFont("Helvetica", 10)

    for idx, row in enumerate(rows, start=1):
        line = f"{idx}. {row['full_name']} | {row['stream_selected']} | Score: {row['merit_score']} | {row['interview_date'] or '-'} {row['interview_time'] or ''}"
        p.drawString(40, y, line)
        y -= 18
        if y < 40:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 40

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="interview_list.pdf", mimetype="application/pdf")


@app.route("/admin/merit-list")
@login_required
def merit_list():
    rows = fetch_merit_sorted(get_db())
    selected = [r for r in rows if r["shortlist_status"] == "Shortlisted for Interview"]
    waiting = [r for r in rows if r["shortlist_status"] == "Waiting List"]
    rejected = [r for r in rows if r["shortlist_status"] == "Not Selected"]
    return render_template("merit_list.html", selected=selected, waiting=waiting, rejected=rejected)


@app.route("/admin/export/csv")
@login_required
def export_csv():
    db = get_db()
    rows = db.execute(
        """
        SELECT s.id, s.full_name, s.category, s.stream_selected, s.service_category,
               m.percentage, ms.merit_score, ms.shortlist_status, s.application_status
        FROM students s
        JOIN marks m ON m.student_id=s.id
        JOIN merit_scores ms ON ms.student_id=s.id
        ORDER BY ms.merit_score DESC
        """
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Application ID", "Name", "Category", "Stream", "Service Category",
        "Percentage", "Merit Score", "Shortlist Status", "Application Status"
    ])
    for row in rows:
        writer.writerow([row["id"], row["full_name"], row["category"], row["stream_selected"], row["service_category"], row["percentage"], row["merit_score"], row["shortlist_status"], row["application_status"]])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name="applications.csv", mimetype="text/csv")


@app.route("/admin/regenerate-merit")
@login_required
def regenerate_merit():
    db = get_db()
    rows = db.execute(
        """
        SELECT s.id as student_id, s.service_category, s.sports_ncc, m.percentage
        FROM students s JOIN marks m ON m.student_id=s.id
        """
    ).fetchall()

    for row in rows:
        merit = calculate_merit(row["percentage"], row["service_category"], row["sports_ncc"])
        db.execute(
            """
            UPDATE merit_scores
            SET percentage_component=?, service_component=?, sports_component=?, merit_score=?, shortlist_status=?
            WHERE student_id=?
            """,
            (*merit, row["student_id"]),
        )
    db.commit()
    flash("Merit list recalculated.", "success")
    return redirect(url_for("merit_list"))


@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)


from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import psycopg2
from psycopg2.extras import RealDictCursor

main = Blueprint("main", __name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "smartcampus"),
        user=os.getenv("DB_USER", "campususer"),
        password=os.getenv("DB_PASSWORD", "campuspass"),
        port=os.getenv("DB_PORT", "5432")
    )

def logged_in():
    return "user_id" in session

@main.route("/")
def index():
    if logged_in():
        return redirect(url_for("main.dashboard"))
    return render_template("index.html", dashboard=False)

@main.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash("Welcome back!", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    except Exception:
        flash("Database connection failed. Please try again.", "error")

    return redirect(url_for("main.index"))

@main.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("main.index"))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT COUNT(*) AS total FROM facilities")
    facility_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM bookings")
    booking_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM bookings WHERE status='Pending'")
    pending_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM maintenance_tickets WHERE status != 'Resolved'")
    active_tickets = cur.fetchone()["total"]

    cur.execute("SELECT * FROM facilities ORDER BY facility_id")
    facilities = cur.fetchall()

    cur.execute("""
        SELECT b.*, f.name AS facility_name, u.name AS user_name
        FROM bookings b
        JOIN facilities f ON b.facility_id=f.facility_id
        JOIN users u ON b.user_id=u.user_id
        ORDER BY b.booking_id DESC
    """)
    bookings = cur.fetchall()

    cur.execute("""
        SELECT t.*, f.name AS facility_name, u.name AS reporter_name,
               tech.name AS technician_name
        FROM maintenance_tickets t
        JOIN facilities f ON t.facility_id=f.facility_id
        JOIN users u ON t.reported_by=u.user_id
        LEFT JOIN users tech ON t.assigned_to=tech.user_id
        ORDER BY t.ticket_id DESC
    """)
    tickets = cur.fetchall()

    cur.execute("SELECT user_id, name FROM users WHERE role='Technician' ORDER BY name")
    technicians = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        dashboard=True,
        name=session["name"],
        role=session["role"],
        facility_count=facility_count,
        booking_count=booking_count,
        pending_count=pending_count,
        active_tickets=active_tickets,
        facilities=facilities,
        bookings=bookings,
        tickets=tickets,
        technicians=technicians
    )

@main.route("/book", methods=["POST"])
def book():
    if not logged_in():
        return redirect(url_for("main.index"))

    facility_id = request.form.get("facility_id")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    purpose = request.form.get("purpose", "").strip()

    if not facility_id or not start_time or not end_time or not purpose:
        flash("Please fill in all booking details.", "error")
        return redirect(url_for("main.dashboard"))

    if start_time >= end_time:
        flash("End time must be after start time.", "error")
        return redirect(url_for("main.dashboard"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE facility_id=%s
        AND status IN ('Approved','Confirmed')
        AND start_time < %s AND end_time > %s
    """, (facility_id, end_time, start_time))

    conflict = cur.fetchone()[0]

    if conflict:
        flash("This facility is already booked for that time.", "error")
    else:
        cur.execute("""
            INSERT INTO bookings (user_id, facility_id, start_time, end_time, purpose, status)
            VALUES (%s,%s,%s,%s,%s,'Pending')
        """, (session["user_id"], facility_id, start_time, end_time, purpose))
        conn.commit()
        flash("Booking request submitted successfully!", "success")

    cur.close()
    conn.close()
    return redirect(url_for("main.dashboard"))

@main.route("/booking/<int:booking_id>/<action>", methods=["POST"])
def booking_action(booking_id, action):
    if not logged_in():
        return redirect(url_for("main.index"))

    if session["role"] not in ["Administrator", "Facility Manager", "Department Approver"]:
        flash("You are not authorised to approve bookings.", "error")
        return redirect(url_for("main.dashboard"))

    if action not in ["approve", "reject"]:
        return redirect(url_for("main.dashboard"))

    new_status = "Approved" if action == "approve" else "Rejected"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE bookings SET status=%s
        WHERE booking_id=%s AND status='Pending'
    """, (new_status, booking_id))

    conn.commit()
    cur.close()
    conn.close()

    flash(f"Booking {new_status.lower()}.", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/ticket", methods=["POST"])
def create_ticket():
    if not logged_in():
        return redirect(url_for("main.index"))

    facility_id = request.form.get("facility_id")
    issue = request.form.get("issue", "").strip()
    priority = request.form.get("priority", "Medium")

    if not facility_id or not issue:
        flash("Please provide the facility and issue details.", "error")
        return redirect(url_for("main.dashboard"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO maintenance_tickets
        (facility_id, reported_by, issue, priority, status)
        VALUES (%s,%s,%s,%s,'Open')
    """, (facility_id, session["user_id"], issue, priority))

    conn.commit()
    cur.close()
    conn.close()

    flash("Maintenance ticket created.", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/ticket/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):
    if not logged_in():
        return redirect(url_for("main.index"))

    if session["role"] not in ["Administrator", "Facility Manager"]:
        flash("Only managers can assign technicians.", "error")
        return redirect(url_for("main.dashboard"))

    technician_id = request.form.get("technician_id")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE maintenance_tickets
        SET assigned_to=%s, status='Assigned'
        WHERE ticket_id=%s
    """, (technician_id, ticket_id))

    conn.commit()
    cur.close()
    conn.close()

    flash("Technician assigned successfully.", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/ticket/<int:ticket_id>/resolve", methods=["POST"])
def resolve_ticket(ticket_id):
    if not logged_in():
        return redirect(url_for("main.index"))

    conn = get_db_connection()
    cur = conn.cursor()

    if session["role"] == "Technician":
        cur.execute("""
            UPDATE maintenance_tickets
            SET status='Resolved'
            WHERE ticket_id=%s AND assigned_to=%s
        """, (ticket_id, session["user_id"]))
    elif session["role"] in ["Administrator", "Facility Manager"]:
        cur.execute("""
            UPDATE maintenance_tickets
            SET status='Resolved'
            WHERE ticket_id=%s
        """, (ticket_id,))
    else:
        flash("You are not authorised to resolve this ticket.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("main.dashboard"))

    conn.commit()
    cur.close()
    conn.close()

    flash("Ticket marked as resolved.", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("main.index"))

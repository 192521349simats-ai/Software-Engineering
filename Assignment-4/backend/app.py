import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

from database import init_db, get_db

app = Flask(__name__)

DB_PATH = os.getenv("DATABASE_PATH", "campus.db")

# Campus configuration
MAX_BOOKING_HOURS = 3
SENSOR_THRESHOLD = 50
SLA_HOURS = 24

ROLES = ["student", "faculty", "admin"]

BOOKING_STATUSES = ["confirmed", "cancelled"]

TICKET_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

ALLOWED_TRANSITIONS = {
    "Open": ["In Progress"],
    "In Progress": ["Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": []
}


def setup():
    init_db()


def error(message, status):
    return jsonify({"error": message}), status


def get_role():
    return request.headers.get("X-Role", "student").lower()


def require_role(*allowed_roles):
    role = get_role()
    if role not in allowed_roles:
        return None
    return role


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


@app.route("/")
def home():
    return jsonify({
        "application": "Smart Campus Facility & Maintenance Platform",
        "status": "running",
        "version": "1.0.0"
    })


# --------------------------------------------------
# FACILITY BOOKING
# --------------------------------------------------

@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}

    facility = data.get("facility")
    user = data.get("user")
    start = parse_datetime(data.get("start"))
    end = parse_datetime(data.get("end"))

    if not facility or not user or not start or not end:
        return error("facility, user, start and end are required", 400)

    if end <= start:
        return error("Booking end must be after start", 400)

    duration = (end - start).total_seconds() / 3600

    if duration > MAX_BOOKING_HOURS:
        return error("Booking duration exceeds 3 hours", 400)

    db = get_db(DB_PATH)

    # Check overlapping bookings
    conflict = db.execute("""
        SELECT id FROM bookings
        WHERE facility = ?
        AND status = 'confirmed'
        AND start_time < ?
        AND end_time > ?
    """, (facility, end.isoformat(), start.isoformat())).fetchone()

    if conflict:
        db.close()
        return error("Facility is already booked for this time", 409)

    cursor = db.execute("""
        INSERT INTO bookings (facility, user, start_time, end_time, status)
        VALUES (?, ?, ?, ?, 'confirmed')
    """, (facility, user, start.isoformat(), end.isoformat()))

    booking_id = cursor.lastrowid
    db.commit()
    db.close()

    return jsonify({
        "message": "Booking created successfully",
        "booking_id": booking_id,
        "facility": facility,
        "status": "confirmed"
    }), 201


@app.route("/bookings", methods=["GET"])
def list_bookings():
    db = get_db(DB_PATH)

    rows = db.execute("""
        SELECT * FROM bookings ORDER BY start_time
    """).fetchall()

    result = [dict(row) for row in rows]
    db.close()

    return jsonify(result), 200


@app.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
def cancel_booking(booking_id):
    role = require_role("student", "faculty", "admin")

    if role is None:
        return error("Unauthorized role", 403)

    db = get_db(DB_PATH)

    booking = db.execute(
        "SELECT * FROM bookings WHERE id = ?", (booking_id,)
    ).fetchone()

    if not booking:
        db.close()
        return error("Booking not found", 404)

    if booking["status"] == "cancelled":
        db.close()
        return error("Booking is already cancelled", 409)

    db.execute("""
        UPDATE bookings SET status = 'cancelled'
        WHERE id = ?
    """, (booking_id,))

    db.commit()
    db.close()

    return jsonify({"message": "Booking cancelled"}), 200


# --------------------------------------------------
# SENSOR MONITORING
# --------------------------------------------------

@app.route("/sensors", methods=["POST"])
def sensor_reading():
    data = request.get_json(silent=True) or {}

    sensor = data.get("sensor")
    value = data.get("value")

    if sensor is None or value is None:
        return error("sensor and value are required", 400)

    try:
        value = float(value)
    except (TypeError, ValueError):
        return error("Sensor value must be numeric", 400)

    if value < 0:
        return error("Sensor value cannot be negative", 400)

    status = "ALERT" if value >= SENSOR_THRESHOLD else "NORMAL"

    db = get_db(DB_PATH)

    db.execute("""
        INSERT INTO sensor_readings (sensor, value, status, recorded_at)
        VALUES (?, ?, ?, ?)
    """, (sensor, value, status, datetime.now().isoformat()))

    db.commit()
    db.close()

    return jsonify({
        "sensor": sensor,
        "value": value,
        "threshold": SENSOR_THRESHOLD,
        "status": status
    }), 201


# --------------------------------------------------
# MAINTENANCE TICKETS
# --------------------------------------------------

@app.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "Medium")

    if not title or not description:
        return error("title and description are required", 400)

    if priority not in ["Low", "Medium", "High", "Critical"]:
        return error("Invalid priority", 400)

    created = datetime.now()

    db = get_db(DB_PATH)

    cursor = db.execute("""
        INSERT INTO tickets
        (title, description, priority, status, created_at)
        VALUES (?, ?, ?, 'Open', ?)
    """, (title, description, priority, created.isoformat()))

    ticket_id = cursor.lastrowid
    db.commit()
    db.close()

    return jsonify({
        "ticket_id": ticket_id,
        "title": title,
        "priority": priority,
        "status": "Open",
        "created_at": created.isoformat(),
        "sla_deadline": (created.replace() + __import__("datetime").timedelta(hours=SLA_HOURS)).isoformat()
    }), 201


@app.route("/tickets", methods=["GET"])
def list_tickets():
    db = get_db(DB_PATH)

    rows = db.execute("""
        SELECT * FROM tickets ORDER BY id DESC
    """).fetchall()

    result = [dict(row) for row in rows]
    db.close()

    return jsonify(result), 200


@app.route("/tickets/<int:ticket_id>/status", methods=["PUT"])
def update_ticket_status(ticket_id):
    role = require_role("faculty", "admin")

    if role is None:
        return error("Only faculty or admin can change ticket status", 403)

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in TICKET_STATUSES:
        return error("Invalid ticket status", 400)

    db = get_db(DB_PATH)

    ticket = db.execute(
        "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
    ).fetchone()

    if not ticket:
        db.close()
        return error("Ticket not found", 404)

    current_status = ticket["status"]

    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        db.close()
        return error(
            f"Invalid transition: {current_status} to {new_status}", 409
        )

    db.execute("""
        UPDATE tickets SET status = ?
        WHERE id = ?
    """, (new_status, ticket_id))

    db.commit()
    db.close()

    return jsonify({
        "ticket_id": ticket_id,
        "previous_status": current_status,
        "status": new_status
    }), 200


# --------------------------------------------------
# SLA MONITORING
# --------------------------------------------------

@app.route("/sla", methods=["GET"])
def sla_report():
    db = get_db(DB_PATH)

    tickets = db.execute("""
        SELECT * FROM tickets
        WHERE status NOT IN ('Resolved', 'Closed')
    """).fetchall()

    now = datetime.now()
    result = []

    for ticket in tickets:
        created = parse_datetime(ticket["created_at"])
        age_hours = (now - created).total_seconds() / 3600 if created else 0

        result.append({
            "ticket_id": ticket["id"],
            "title": ticket["title"],
            "priority": ticket["priority"],
            "age_hours": round(age_hours, 2),
            "sla_hours": SLA_HOURS,
            "sla_breached": age_hours > SLA_HOURS
        })

    db.close()
    return jsonify(result), 200


if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0", port=5000, debug=False)

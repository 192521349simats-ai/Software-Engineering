def test_booking_saved_and_retrievable(client):
    booking = {
        "facility": "Library Hall",
        "user": "Student1",
        "start": "2026-11-23T09:00:00",
        "end": "2026-11-23T10:00:00"
    }

    created = client.post("/bookings", json=booking)
    assert created.status_code == 201

    bookings = client.get("/bookings")
    assert bookings.status_code == 200
    assert any(b["facility"] == "Library Hall" for b in bookings.json)


def test_overlapping_booking_rejected(client):
    booking = {
        "facility": "Lab A",
        "user": "Student1",
        "start": "2026-11-23T09:00:00",
        "end": "2026-11-23T10:00:00"
    }

    first = client.post("/bookings", json=booking)
    assert first.status_code == 201

    second = client.post("/bookings", json={
        **booking,
        "user": "Student2",
        "start": "2026-11-23T09:30:00",
        "end": "2026-11-23T10:30:00"
    })
    assert second.status_code == 409


def test_ticket_creation_and_retrieval(client):
    created = client.post("/tickets", json={
        "title": "Projector Failure",
        "description": "Projector is not working in Room 2",
        "priority": "High"
    })
    assert created.status_code == 201
    ticket_id = created.json["ticket_id"]

    tickets = client.get("/tickets")
    assert tickets.status_code == 200
    assert any(t["id"] == ticket_id for t in tickets.json)


def test_ticket_status_role_authorization(client):
    created = client.post("/tickets", json={
        "title": "Broken Fan",
        "description": "Fan needs maintenance",
        "priority": "Medium"
    })
    ticket_id = created.json["ticket_id"]

    denied = client.put(
        f"/tickets/{ticket_id}/status",
        json={"status": "In Progress"},
        headers={"X-Role": "student"}
    )
    assert denied.status_code == 403

    allowed = client.put(
        f"/tickets/{ticket_id}/status",
        json={"status": "In Progress"},
        headers={"X-Role": "faculty"}
    )
    assert allowed.status_code == 200
    assert allowed.json["status"] == "In Progress"

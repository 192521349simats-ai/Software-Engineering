def test_booking_exactly_three_hours_allowed(client):
    response = client.post("/bookings", json={
        "facility": "Lab Boundary",
        "user": "Student1",
        "start": "2026-11-23T09:00:00",
        "end": "2026-11-23T12:00:00"
    })
    assert response.status_code == 201


def test_sensor_below_threshold_is_normal(client):
    response = client.post("/sensors", json={
        "sensor": "Temperature",
        "value": 49.9
    })
    assert response.status_code == 201
    assert response.json["status"] == "NORMAL"


def test_invalid_ticket_transition_rejected(client):
    created = client.post("/tickets", json={
        "title": "Maintenance Test",
        "description": "Regression test ticket",
        "priority": "Medium"
    })
    ticket_id = created.json["ticket_id"]

    response = client.put(
        f"/tickets/{ticket_id}/status",
        json={"status": "Closed"},
        headers={"X-Role": "admin"}
    )
    assert response.status_code == 409


def test_booking_cannot_be_cancelled_twice(client):
    created = client.post("/bookings", json={
        "facility": "Room B",
        "user": "Student1",
        "start": "2026-11-24T09:00:00",
        "end": "2026-11-24T10:00:00"
    })
    booking_id = created.json["booking_id"]

    first = client.put(
        f"/bookings/{booking_id}/cancel",
        headers={"X-Role": "student"}
    )
    assert first.status_code == 200

    second = client.put(
        f"/bookings/{booking_id}/cancel",
        headers={"X-Role": "student"}
    )
    assert second.status_code == 409

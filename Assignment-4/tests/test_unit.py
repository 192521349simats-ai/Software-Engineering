def test_booking_missing_fields(client):
    response = client.post("/bookings", json={})
    assert response.status_code == 400


def test_booking_end_before_start(client):
    response = client.post("/bookings", json={
        "facility": "Lab A",
        "user": "Student1",
        "start": "2026-11-23T12:00:00",
        "end": "2026-11-23T11:00:00"
    })
    assert response.status_code == 400


def test_booking_exceeds_maximum_duration(client):
    response = client.post("/bookings", json={
        "facility": "Lab A",
        "user": "Student1",
        "start": "2026-11-23T09:00:00",
        "end": "2026-11-23T13:00:00"
    })
    assert response.status_code == 400


def test_sensor_non_numeric_value(client):
    response = client.post("/sensors", json={
        "sensor": "Temperature",
        "value": "invalid"
    })
    assert response.status_code == 400


def test_sensor_negative_value(client):
    response = client.post("/sensors", json={
        "sensor": "Temperature",
        "value": -5
    })
    assert response.status_code == 400


def test_sensor_threshold_alert(client):
    response = client.post("/sensors", json={
        "sensor": "Temperature",
        "value": 50
    })
    assert response.status_code == 201
    assert response.json["status"] == "ALERT"

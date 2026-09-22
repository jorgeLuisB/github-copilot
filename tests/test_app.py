from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == (
        "Learn strategies and compete in chess tournaments"
    )
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Chess Club"]["max_participants"] == 12
    assert "participants" in payload["Chess Club"]


def test_signup_adds_participant():
    email = "new@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post("/activities/Unknown Club/signup?email=new@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant():
    email = "michael@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_when_activity_is_full():
    activities["Chess Club"]["participants"] = [
        f"student{i}@mergington.edu" for i in range(2)
    ]
    activities["Chess Club"]["max_participants"] = 2

    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_delete_signup_removes_participant():
    activities["Chess Club"]["participants"] = [
        "alice@mergington.edu",
        "bob@mergington.edu",
    ]

    response = client.delete("/activities/Chess Club/signup?email=alice@mergington.edu")

    assert response.status_code == 200
    assert "alice@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Removed alice@mergington.edu from Chess Club"


def test_delete_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_rejects_unregistered_participant():
    response = client.delete(
        "/activities/Chess Club/signup?email=not-signed-up@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"

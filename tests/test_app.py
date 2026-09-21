from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_rejects_duplicate_participant():
    email = "michael@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_when_activity_is_full():
    original_activity = activities["Chess Club"]
    original_participants = list(original_activity["participants"])
    original_limit = original_activity["max_participants"]

    try:
        activities["Chess Club"]["participants"] = [
            f"student{i}@mergington.edu" for i in range(2)
        ]
        activities["Chess Club"]["max_participants"] = 2

        response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")

        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    finally:
        activities["Chess Club"]["participants"] = original_participants
        activities["Chess Club"]["max_participants"] = original_limit


def test_delete_signup_removes_participant():
    original_activity = activities["Chess Club"]
    original_participants = list(original_activity["participants"])

    try:
        activities["Chess Club"]["participants"] = [
            "alice@mergington.edu",
            "bob@mergington.edu",
        ]

        response = client.delete("/activities/Chess Club/signup?email=alice@mergington.edu")

        assert response.status_code == 200
        assert "alice@mergington.edu" not in activities["Chess Club"]["participants"]
        assert response.json()["message"] == "Removed alice@mergington.edu from Chess Club"
    finally:
        activities["Chess Club"]["participants"] = original_participants

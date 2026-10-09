from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email():
    activity_name = "Chess Club"
    email = "new-test-student@mergington.edu"

    if email not in client.get("/activities").json()[activity_name]["participants"]:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found():
    activity_name = "Programming Class"
    email = "missing-student@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    assert response.status_code == 404

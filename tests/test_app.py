from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities_data(monkeypatch):
    activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activities_data):
    return TestClient(app_module.app)


def test_get_activities_returns_all_activity_details(client, activities_data):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities_data


def test_signup_adds_participant(client, activities_data):
    # Arrange
    activity_name = "Chess Club"
    email = "new-test-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate_participant_returns_bad_request(client, activities_data):
    # Arrange
    activity_name = "Chess Club"
    email = activities_data[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities_data[activity_name]["participants"].count(email) == 1


def test_signup_unknown_activity_returns_not_found(client, activities_data):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new-test-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_name not in activities_data


def test_unregister_participant_removes_email(client, activities_data):
    # Arrange
    activity_name = "Chess Club"
    email = "new-test-student@mergington.edu"
    activities_data[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found(client, activities_data):
    # Arrange
    activity_name = "Programming Class"
    email = "missing-student@mergington.edu"
    participants_before = activities_data[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found in this activity"}
    assert activities_data[activity_name]["participants"] == participants_before


def test_unregister_unknown_activity_returns_not_found(client, activities_data):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_name not in activities_data

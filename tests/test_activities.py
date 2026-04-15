import pytest


def test_get_all_activities_success(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    activity = data["Chess Club"]
    assert activity["description"] == "Learn strategies and compete in chess tournaments"
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


def test_get_activities_response_format(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for details in data.values():
        assert isinstance(details, dict)
        assert all(key in details for key in ["description", "schedule", "max_participants", "participants"])
        assert isinstance(details["participants"], list)


def test_signup_success(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    second_response = client.get("/activities")
    participants = second_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_activity_not_found(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/NonExistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_duplicate_prevention(client):
    # Arrange
    email = "emma@mergington.edu"

    # Act
    response = client.post("/activities/Programming%20Class/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    second_response = client.get("/activities")
    participants = second_response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_activity_not_found(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/NonExistent/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered(client):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_participant_removed(client):
    # Arrange
    email = "daniel@mergington.edu"
    remaining_email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = client.get("/activities").json()["Chess Club"]
    assert email not in data["participants"]
    assert remaining_email in data["participants"]


def test_signup_then_unregister_flow(client):
    # Arrange
    email = "studentflow@mergington.edu"

    # Act
    signup_response = client.post("/activities/Gym%20Class/signup", params={"email": email})
    get_response = client.get("/activities")
    unregister_response = client.delete("/activities/Gym%20Class/unregister", params={"email": email})
    final_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert email in get_response.json()["Gym Class"]["participants"]
    assert unregister_response.status_code == 200
    assert email not in final_response.json()["Gym Class"]["participants"]


def test_multiple_participants_different_emails(client):
    # Arrange
    new_email = "newparticipant@mergington.edu"
    existing_email = "michael@mergington.edu"

    # Act
    signup_response = client.post("/activities/Chess%20Club/signup", params={"email": new_email})
    unregister_response = client.delete("/activities/Chess%20Club/unregister", params={"email": existing_email})

    # Assert
    assert signup_response.status_code == 200
    data = client.get("/activities").json()["Chess Club"]
    assert new_email in data["participants"]
    assert existing_email not in data["participants"]


def test_email_case_consistency(client):
    # Arrange
    lower_email = "casecheck@mergington.edu"
    signup_response = client.post("/activities/Gym%20Class/signup", params={"email": lower_email})

    # Act
    unregister_response = client.delete("/activities/Gym%20Class/unregister", params={"email": lower_email.upper()})

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code in (200, 400)
    assert unregister_response.json()["detail"] in ("Student is not registered for this activity",)

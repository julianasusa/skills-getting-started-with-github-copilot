import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state after each test"""
    original_activities = activities.copy()
    yield
    activities.clear()
    activities.update(original_activities)


client = TestClient(app)


def test_get_root():
    """Test root endpoint serves the static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on current data
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup"""
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up test@example.com for Chess Club" == result["message"]

    # Verify added to participants
    response2 = client.get("/activities")
    data = response2.json()
    assert "test@example.com" in data["Chess Club"]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_signup_already_signed_up():
    """Test signup when already registered"""
    # First signup
    client.post("/activities/Chess Club/signup?email=test2@example.com")

    # Try again
    response = client.post("/activities/Chess Club/signup?email=test2@example.com")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student already signed up"


def test_unregister_success():
    """Test successful unregister"""
    # First signup
    client.post("/activities/Chess Club/signup?email=test3@example.com")

    # Then unregister
    response = client.delete("/activities/Chess Club/signup?email=test3@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered test3@example.com from Chess Club" == result["message"]

    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert "test3@example.com" not in data["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    """Test unregister when not signed up"""
    response = client.delete("/activities/Chess Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student not signed up"
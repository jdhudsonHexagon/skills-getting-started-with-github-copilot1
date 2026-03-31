import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database before each test"""
    # Store original state
    original_activities = {}
    for activity_name, activity_data in activities.items():
        original_activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }

    yield

    # Reset to original state after test
    activities.clear()
    activities.update(original_activities)


class TestActivitiesAPI:
    """Test cases for the activities API endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Check that we get the expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

        # Check structure of activity data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_has_correct_data(self, client):
        """Test that activities have the correct initial data"""
        response = client.get("/activities")
        data = response.json()

        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up test@mergington.edu for Basketball Team" in data["message"]

        # Verify the participant was added
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "test@mergington.edu" in activities_data["Basketball Team"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test signing up a participant who is already registered"""
        # First signup
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "test@mergington.edu"}
        )

        # Try to signup again
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already registered for this activity" in data["detail"]

    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        # First signup
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "test@mergington.edu"}
        )

        # Then unregister
        response = client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered test@mergington.edu from Basketball Team" in data["message"]

        # Verify the participant was removed
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "test@mergington.edu" not in activities_data["Basketball Team"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_non_participant(self, client):
        """Test unregistration of a student who is not registered"""
        response = client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is not registered for this activity" in data["detail"]

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static HTML"""
        # Disable following redirects to check the redirect status
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
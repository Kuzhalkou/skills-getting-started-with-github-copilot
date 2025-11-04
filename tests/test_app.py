import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [301, 302, 307]  # Any redirect status is acceptable
    assert response.headers["location"].endswith("/static/index.html")

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check structure of an activity
    activity = list(data.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"

    # Verify the student was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using an email we know exists
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    activity_name = "Non Existent Club"
    email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_unregister_success():
    """Test successful activity unregistration"""
    # First sign up a test student
    activity_name = "Chess Club"
    email = "test_unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Now try to unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"

    # Verify the student was actually removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    activity_name = "Non Existent Club"
    email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
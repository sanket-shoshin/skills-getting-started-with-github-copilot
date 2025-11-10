from fastapi.testclient import TestClient
import copy

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_data():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should contain at least one known activity
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Backup activities to restore after test
    backup = copy.deepcopy(activities)
    try:
        # Ensure the email is not present
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

        # Sign up
        resp = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp.status_code == 200
        assert email in activities[activity]["participants"]

        # Duplicate signup should fail
        resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp2.status_code == 400

        # Unregister
        resp3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert resp3.status_code == 200
        assert email not in activities[activity]["participants"]

        # Unregistering again should return 400
        resp4 = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert resp4.status_code == 400

    finally:
        # Restore original activities state
        activities.clear()
        activities.update(backup)

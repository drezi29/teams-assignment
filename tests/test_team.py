from src.messages import TEAM_CREATED_SUCCESFULLY_MSG

TEST_TEAM_NAME = "Test Team"

def test_create_team_without_parent(test_client):
    data = {"name": TEST_TEAM_NAME}
    response = test_client.post("/teams/", json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == TEAM_CREATED_SUCCESFULLY_MSG
    
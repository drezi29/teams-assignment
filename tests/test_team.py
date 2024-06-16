from .utils import get_random_id
from .utils import TEST_TEAM_NAME
from src.messages import (
    PARENT_TEAM_NOT_FOUND_ERROR,
    TEAM_CREATED_SUCCESFULLY_MSG
)


def test_create_team_without_parent(test_client):
    response_data = {"name": TEST_TEAM_NAME}
    response = test_client.post("/teams/", json=response_data)
    
    data = response.json()
    assert response.status_code == 201
    assert data["message"] == TEAM_CREATED_SUCCESFULLY_MSG


def test_create_team_with_parent(test_client, create_basic_records):
    (team_parent, *_) = create_basic_records
    response_data = {"name": TEST_TEAM_NAME, "parent_team_id": str(team_parent.id)}
    response = test_client.post("/teams/", json=response_data)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == TEAM_CREATED_SUCCESFULLY_MSG


def test_create_team_with_not_existing_parent(test_client):
    response_data = {"name": TEST_TEAM_NAME, "parent_team_id": str(get_random_id())}
    response = test_client.post("/teams/", json=response_data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == PARENT_TEAM_NOT_FOUND_ERROR

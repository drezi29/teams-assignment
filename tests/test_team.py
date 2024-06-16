from src.messages import (
    PARENT_TEAM_NOT_FOUND_ERROR,
    TEAM_CREATED_SUCCESFULLY_MSG,
    TEAM_WITH_NAME_EXISTS,
)

from .utils import (
    TEST_TEAM_CHILD_NAME,
    TEST_TEAM_NAME,
    TEST_TEAM_PARENT_NAME,
    TEST_TEAM_WITHOUT_PARENT_NAME,
    get_random_id,
)


def test_create_team_without_parent(test_client):
    response_data = {"name": TEST_TEAM_NAME}
    response = test_client.post("/teams/", json=response_data)

    data = response.json()
    assert response.status_code == 201
    assert data["message"] == TEAM_CREATED_SUCCESFULLY_MSG

    get_teams_response = test_client.get("/teams/")
    data_get = get_teams_response.json()

    assert len(data_get) == 1
    assert data_get[0]["name"] == TEST_TEAM_NAME
    assert data_get[0]["parent_team"] == None


def test_create_team_with_parent(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    team_parent_id = str(team_parent.id)

    response_data = {"name": TEST_TEAM_NAME, "parent_team_id": team_parent_id}
    response = test_client.post("/teams/", json=response_data)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == TEAM_CREATED_SUCCESFULLY_MSG

    get_teams_response = test_client.get("/teams/")
    data_get = get_teams_response.json()

    assert len(data_get) == 4
    assert data_get[-1]["name"] == TEST_TEAM_NAME
    assert data_get[-1]["parent_team"] == team_parent_id


def test_create_team_with_not_existing_parent(test_client):
    response_data = {"name": TEST_TEAM_NAME, "parent_team_id": str(get_random_id())}
    response = test_client.post("/teams/", json=response_data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == PARENT_TEAM_NOT_FOUND_ERROR


def test_create_team_with_not_unique_name(test_client, create_basic_records):
    response_data = {"name": TEST_TEAM_PARENT_NAME}
    response = test_client.post("/teams/", json=response_data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == TEAM_WITH_NAME_EXISTS


def test_get_teams_without_data(test_client):
    response = test_client.get("/teams/")
    assert response.status_code == 204


def test_get_teams_with_data(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    response = test_client.get("/teams/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == TEST_TEAM_CHILD_NAME
    assert data[0]["parent_team"] == str(team_parent.id)
    assert data[1]["name"] == TEST_TEAM_PARENT_NAME
    assert data[1]["parent_team"] == None
    assert data[2]["name"] == TEST_TEAM_WITHOUT_PARENT_NAME
    assert data[2]["parent_team"] == None

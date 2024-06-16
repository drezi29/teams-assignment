from .utils import (
    TEST_EXPERIMENT_DESCRIPTION,
    TEST_TEAM_WITHOUT_PARENT_NAME,
    TEST_TEAM_CHILD_NAME
    )
from src.main import app
from src.messages import (
    EXPERIMENT_CREATED_SUCCESSFULLY_MSG,
    TEAM_BY_NAME_NOT_FOUND_ERROR
)

def test_create_experiment(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    team_parent_id = str(team_parent.id)
    team_parent_name = team_parent.name

    sample_ratio = 0.5
    allowed_team_assignments = 1

    response_data = {
        "description": TEST_EXPERIMENT_DESCRIPTION,
        "sample_ratio": sample_ratio,
        "allowed_team_assignments": allowed_team_assignments,
        "team_ids": [team_parent_id]
    }
    response = test_client.post("/experiments/", json=response_data)
    assert response.status_code == 201
    data = response.json()
    assert "experiment_id" in data
    assert data["message"] == EXPERIMENT_CREATED_SUCCESSFULLY_MSG

    get_experiments_response = test_client.get("/experiments/")
    data_get = get_experiments_response.json()

    assert len(data_get) == 3
    assert data_get[2]["description"] == TEST_EXPERIMENT_DESCRIPTION
    assert data_get[2]["sample_ratio"] == sample_ratio
    assert data_get[2]["allowed_team_assignments"] == allowed_team_assignments

    experiment_teams = data_get[2]["teams"]
    assert len(experiment_teams) == 1
    assert experiment_teams[0]["name"] == team_parent_name
    assert experiment_teams[0]["id"] == team_parent_id


def test_get_experiments_without_data(test_client):
    response = test_client.get("/experiments/")
    assert response.status_code == 204


def test_get_teams_with_data(test_client, create_basic_records):
    team_parent, team_child, team_without_parent, experiment1, experiment2 = create_basic_records
    response = test_client.get("/experiments/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["description"] == experiment1.description
    assert data[0]["sample_ratio"] == experiment1.sample_ratio
    assert data[0]["allowed_team_assignments"] == experiment1.allowed_team_assignments
    experiment1_teams = data[0]["teams"]
    assert len(experiment1_teams) == 1

    assert data[1]["description"] == experiment2.description
    assert data[1]["sample_ratio"] == experiment2.sample_ratio
    assert data[1]["allowed_team_assignments"] == experiment2.allowed_team_assignments
    experiment2_teams = data[1]["teams"]
    assert len(experiment2_teams) == 2


def test_get_teams_with_filter(test_client, create_basic_records):
    response = test_client.get(
        "/experiments/", 
        params={"team_name": TEST_TEAM_WITHOUT_PARENT_NAME}
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert len(data[0]["teams"]) == 1
    assert data[0]["teams"][0]["name"] == TEST_TEAM_WITHOUT_PARENT_NAME
    assert len(data[1]["teams"]) == 2
    assert data[1]["teams"][0]["name"] == TEST_TEAM_WITHOUT_PARENT_NAME


def test_get_teams_with_filter_child_name(test_client, create_basic_records):
    response = test_client.get(
        "/experiments/", 
        params={"team_name": TEST_TEAM_CHILD_NAME}
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["teams"]) == 2
    assert data[0]["teams"][0]["name"] == TEST_TEAM_WITHOUT_PARENT_NAME


def test_get_teams_with_filter_not_existing_name(test_client, create_basic_records):
    response = test_client.get(
        "/experiments/", 
        params={"team_name": "Not existing team name"}
        )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == TEAM_BY_NAME_NOT_FOUND_ERROR

from .utils import get_random_id
from .utils import (
    TEST_EXPERIMENT_DESCRIPTION,
    TEST_TEAM_WITHOUT_PARENT_NAME,
    TEST_TEAM_CHILD_NAME
    )
from src.main import app
from src.messages import (
    ASSIGNMENTS_UPDATED_MSG,
    CANNOT_ASSIGN_CHILD_WITH_PARENT_TO_EXPERIMENT_ERROR,
    EXPERIMENT_CREATED_SUCCESSFULLY_MSG,
    EXPERIMENT_NOT_FOUND_ERROR,
    TEAM_BY_NAME_NOT_FOUND_ERROR,
    VALUE_OF_ALLOWED_TEAM_ASSIGNMNETS_RANGE_ERROR,
    INVALID_ASSIGNMENTS_AMOUNT,
    TEAMS_NOT_FOUND
)
from src.config import MIN_ALLOWED_TEAMS, MAX_ALLOWED_TEAMS

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


def test_create_experiment_validation_allowed_team_assignments(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    team_parent_id = str(team_parent.id)

    sample_ratio = 0.5
    allowed_team_assignments = MAX_ALLOWED_TEAMS + 1

    response_data = {
        "description": TEST_EXPERIMENT_DESCRIPTION,
        "sample_ratio": sample_ratio,
        "allowed_team_assignments": allowed_team_assignments,
        "team_ids": [team_parent_id]
    }
    response = test_client.post("/experiments/", json=response_data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == VALUE_OF_ALLOWED_TEAM_ASSIGNMNETS_RANGE_ERROR.format(
                    min=MIN_ALLOWED_TEAMS, max=MAX_ALLOWED_TEAMS
                    )


def test_create_experiment_validation_of_assigned_teams(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    team_parent_id = str(team_parent.id)

    sample_ratio = 0.5
    allowed_team_assignments = 2

    response_data = {
        "description": TEST_EXPERIMENT_DESCRIPTION,
        "sample_ratio": sample_ratio,
        "allowed_team_assignments": allowed_team_assignments,
        "team_ids": [team_parent_id]
    }
    response = test_client.post("/experiments/", json=response_data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == INVALID_ASSIGNMENTS_AMOUNT.format(
        allowed_assignments=allowed_team_assignments
        )


def test_create_experiment_validation_of_assigning_team_existence(test_client):
    sample_ratio = 0.5
    allowed_team_assignments = 1
    team_ids = [str(get_random_id())]

    response_data = {
        "description": TEST_EXPERIMENT_DESCRIPTION,
        "sample_ratio": sample_ratio,
        "allowed_team_assignments": allowed_team_assignments,
        "team_ids": team_ids
    }
    response = test_client.post("/experiments/", json=response_data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == TEAMS_NOT_FOUND.format(ids=set(team_ids))


def test_create_experiment_validation_of_assigning_team_and_its_child(test_client, create_basic_records):
    team_parent, team_child, team_without_parent, experiment1, experiment2 = create_basic_records
    sample_ratio = 0.5
    allowed_team_assignments = 2
    team_parent_id = str(team_parent.id)
    team_child_id = str(team_child.id)

    response_data = {
        "description": TEST_EXPERIMENT_DESCRIPTION,
        "sample_ratio": sample_ratio,
        "allowed_team_assignments": allowed_team_assignments,
        "team_ids": [team_parent_id, team_child_id]
    }
    response = test_client.post("/experiments/", json=response_data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == CANNOT_ASSIGN_CHILD_WITH_PARENT_TO_EXPERIMENT_ERROR


def test_get_experiments_without_data(test_client):
    response = test_client.get("/experiments/")
    assert response.status_code == 204


def test_get_teams_with_data(test_client, create_basic_records):
    *_, experiment1, experiment2 = create_basic_records
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


def test_update_assignments_positive_scenario(test_client, create_basic_records):
    team_parent, team_child, team_without_parent, experiment1, experiment2 = create_basic_records
    experiment_id = str(experiment1.id)
    team_ids = [str(team_parent.id)]

    params = {
        "team_ids": team_ids
    }
    response = test_client.put(f"/experiments/{experiment_id}/teams", params=params)
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == ASSIGNMENTS_UPDATED_MSG


def test_update_assignments_with_not_existing_experiment(test_client, create_basic_records):
    team_parent, *_ = create_basic_records
    team_ids = [str(team_parent.id)]
    experiment_id = str(get_random_id())
    params = {
        "team_ids": team_ids
    }
    response = test_client.put(f"/experiments/{experiment_id}/teams", params=params)
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == EXPERIMENT_NOT_FOUND_ERROR

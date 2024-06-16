import uuid

TEST_EXPERIMENT_DESCRIPTION = "Test Experiment"
TEST_TEAM_NAME = "Test Team"
TEST_TEAM_PARENT_NAME = "Team parent"
TEST_TEAM_CHILD_NAME = "Team child"
TEST_TEAM_WITHOUT_PARENT_NAME = "Team without parent"


def get_random_id() -> uuid.UUID:
    return uuid.uuid4()

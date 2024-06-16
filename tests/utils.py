import uuid


TEST_TEAM_NAME = "Test Team"


def get_random_id() -> uuid.UUID:
    return uuid.uuid4()

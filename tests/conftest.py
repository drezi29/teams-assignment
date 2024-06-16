from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Any, Generator
import pytest
import uuid

from src.database import Base
from src.main import app, get_db
from src.models import Experiment, Team

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/test_db"

engine = create_engine(
    TEST_DATABASE_URL
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def create_basic_records(db_session):
    team_parent = Team(id=get_random_id(), name="Team parent")
    team_child = Team(id=get_random_id(), name="Team child", parent_team=team_parent.id)
    team_without_parent = Team(id=get_random_id(), name="Team without parent")

    db_session.add(team_parent)
    db_session.add(team_child)
    db_session.add(team_without_parent)
    db_session.commit()
    db_session.refresh(team_parent)
    db_session.refresh(team_child)
    db_session.refresh(team_without_parent)

    teams_for_experiment1 = [team_without_parent]
    teams_for_experiment2 = [team_child, team_without_parent]
    experiment1 = Experiment(
        id=get_random_id(),
        description="Experiment 1",
        sample_ratio=0.5,
        allowed_team_assignments=1
    )
    experiment2 = Experiment(
        id=get_random_id(),
        description="Experiment 2",
        sample_ratio=0.8,
        allowed_team_assignments=2
    )

    db_session.add(experiment1)
    db_session.add(experiment2)
    experiment1.teams.append(team_without_parent)
    experiment2.teams.append(team_without_parent)
    experiment2.teams.append(team_child)
    db_session.commit()
    db_session.refresh(experiment1)
    db_session.refresh(experiment2)

    yield team_parent, team_child, team_without_parent, experiment1, experiment2


def get_random_id() -> uuid.UUID:
    return uuid.uuid4()

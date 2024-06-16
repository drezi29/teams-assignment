from sqlalchemy import UUID, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

team_experiment_assignment = Table(
    'team_experiment_assignment',
    Base.metadata,
    Column('team_id', UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True),
    Column(
        'experiment_id',
        UUID(as_uuid=True),
        ForeignKey('experiments.id'),
        primary_key=True,
    ),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, unique=True)
    parent_team = Column(UUID, ForeignKey("teams.id"))

    experiments = relationship(
        "Experiment", secondary=team_experiment_assignment, back_populates="teams"
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True)
    description = Column(String)
    sample_ratio = Column(Float)
    allowed_team_assignments = Column(Integer)

    teams = relationship(
        "Team", secondary=team_experiment_assignment, back_populates="experiments"
    )

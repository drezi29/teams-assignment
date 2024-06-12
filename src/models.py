from sqlalchemy import Column, Float, ForeignKey, Integer, String, UUID

from database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID, primary_key=True)
    name = Column(String, unique=True)
    parent_team = Column(UUID, ForeignKey("teams.id"))


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID, primary_key=True)
    description = Column(String)
    sample_ratio = Column(Float)
    allowed_team_assignments = Column(Integer)


class TeamExperimentAssignment(Base):
    __tablename__ = "teamexperiments"

    team_id = Column(UUID, ForeignKey("teams.id"), primary_key=True)
    experiment_id = Column(UUID, ForeignKey("experiments.id"), primary_key=True)


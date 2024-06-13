from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, contains_eager, Session
import uuid

from . import models
from .constants import MIN_ALLOWED_TEAMS, MAX_ALLOWED_TEAMS

def get_experiments(db: Session, team_name: str | None, limit: int = 100):
    query = db.query(models.Experiment)\
        .join(models.Experiment.teams)\
        .options(contains_eager(models.Experiment.teams).load_only(models.Team.id, models.Team.name))\
    
    if team_name:
        query = query.filter(models.Team.name == team_name)

    return query.limit(limit).all()


def create_experiment(db: Session, description: str, sample_ratio: float, allowed_team_assignments: int):
    if not (MIN_ALLOWED_TEAMS <= allowed_team_assignments <= MAX_ALLOWED_TEAMS):
        raise HTTPException(status_code=400, detail=f"Value of allowed team assignments has to be between {MIN_ALLOWED_TEAMS} and {MAX_ALLOWED_TEAMS}")
    
    db_experiment = models.Experiment(
        id=str(uuid.uuid4()),
        description=description,
        sample_ratio=sample_ratio,
        allowed_team_assignments=allowed_team_assignments
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return db_experiment


def get_teams(db: Session, limit: int = 100):
    return db.query(models.Team).options(selectinload(models.Team.experiments).load_only(models.Experiment.id, models.Experiment.description)).limit(limit).all()


def create_team(db: Session, name: str):
    db_team = models.Team(
        id=str(uuid.uuid4()),
        name=name
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def create_assignment(db: Session, team_id: str, experiment_id: str):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    experiment = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    team.experiments.append(experiment)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Assignment already exists")
    
    return {"team_id": team_id, "experiment_id": experiment_id}

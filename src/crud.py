from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import uuid

from . import models


def get_experiments(db: Session, limit: int = 100):
    return db.query(models.Experiment).limit(limit).all()


def create_experiment(db: Session, description: str, sample_ratio: float, allowed_team_assignments: int):
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
    return db.query(models.Team).limit(limit).all()


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

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
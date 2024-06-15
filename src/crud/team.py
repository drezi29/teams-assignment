from fastapi import HTTPException
from sqlalchemy.orm import selectinload, Session
import uuid

from ..models import Team, Experiment
from ..messages import PARENT_TEAM_NOT_FOUND_ERROR, TEAM_CREATED_SUCCESFULLY_MSG


def get_teams(limit: int, db: Session):
    query = (
        db.query(Team)
        .options(
            selectinload(Team.experiments)
            .load_only(Experiment.id, Experiment.description)
        )
        .limit(limit)
        .all()
    )

    return query


def create_team(db: Session, name: str, parent_team_id: str | None):
    if parent_team_id:
        parent_team_from_db = db.query(Team).filter(Team.id == parent_team_id).first()
        if not parent_team_from_db:
            raise HTTPException(status_code=404, detail=PARENT_TEAM_NOT_FOUND_ERROR)
    
    db_team = Team(
        id=str(uuid.uuid4()),
        name=name,
        parent_team=parent_team_id
    )

    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    return {
        "message": TEAM_CREATED_SUCCESFULLY_MSG,
        "team_id": str(db_team.id),
        "name": db_team.name,
        "parent_team_id": str(db_team.parent_team) if db_team.parent_team else None
    }

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, Session
import uuid

from ..messages import (
    PARENT_TEAM_NOT_FOUND_ERROR,
    TEAM_CREATED_SUCCESFULLY_MSG,
    TEAM_WITH_NAME_EXISTS,
    UNEXPECTED_ERROR
)
from ..models import Experiment, Team


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


def create_team(name: str, parent_team_id: str | None, db: Session):
    check_if_parent_team_exists(parent_team_id, db)
    check_if_name_unique(name, db)
    db_team = Team(
        id=str(uuid.uuid4()),
        name=name,
        parent_team=parent_team_id
    )
    db.add(db_team)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=UNEXPECTED_ERROR)
    
    db.refresh(db_team)

    return {
        "message": TEAM_CREATED_SUCCESFULLY_MSG,
        "team_id": str(db_team.id),
    }


def check_if_parent_team_exists(parent_team_id: str, db: Session):
    if parent_team_id:
        parent_team_from_db = db.query(Team).filter(Team.id == parent_team_id).first()
        if not parent_team_from_db:
            raise HTTPException(status_code=404, detail=PARENT_TEAM_NOT_FOUND_ERROR)


def check_if_name_unique(name: str, db: Session):
    teams_with_same_name = db.query(Team).filter(Team.name == name).first()
    if teams_with_same_name:
        raise HTTPException(status_code=400, detail=TEAM_WITH_NAME_EXISTS)
    
from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, Session
import uuid

from ..messages import (
    PARENT_TEAM_NOT_FOUND_ERROR,
    TEAM_CREATED_SUCCESFULLY_MSG,
    TEAM_WITH_NAME_EXISTS,
)
from ..models import Experiment, Team


def get_teams(db: Session, limit: int):
    query = (
        db.query(Team)
        .options(
            selectinload(Team.experiments)
            .load_only(Experiment.id, Experiment.description)
        )
        .order_by(asc(Team.name))
        .limit(limit)
        .all()
    )

    return query


def create_team(db: Session, name: str, parent_team_id: str | None):
    db_team = Team(
        id=str(uuid.uuid4()),
        name=name,
        parent_team=parent_team_id
    )
    db.add(db_team)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        error_info = str(e.orig)
        if 'violates unique constraint "teams_name_key"' in error_info:
            raise HTTPException(status_code=400, detail=TEAM_WITH_NAME_EXISTS)
        elif 'violates foreign key constraint "teams_parent_team_fkey' in error_info:
            raise HTTPException(status_code=404, detail=PARENT_TEAM_NOT_FOUND_ERROR)
        else:
            raise HTTPException(status_code=400, detail='IntegrityError occurred: {error_info}')
    
    db.refresh(db_team)

    return {
        "message": TEAM_CREATED_SUCCESFULLY_MSG,
        "team_id": str(db_team.id),
    }

    
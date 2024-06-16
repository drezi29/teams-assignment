from fastapi import HTTPException
from sqlalchemy import asc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session
import uuid

from ..messages import (
    ASSIGNMENTS_ALREADY_EXISTS_ERROR,
    ASSIGNMENTS_UPDATED_MSG,
    CANNOT_ASSIGN_CHILD_WITH_PARENT_TO_EXPERIMENT_ERROR,
    EXPERIMENT_CREATED_SUCCESSFULLY_MSG,
    EXPERIMENT_NOT_FOUND_ERROR,
    INVALID_ASSIGNMENTS_AMOUNT,
    TEAM_BY_NAME_NOT_FOUND_ERROR,
    TEAMS_NOT_FOUND,
    UNEXPECTED_ERROR,
    VALUE_OF_ALLOWED_TEAM_ASSIGNMNETS_RANGE_ERROR
)
from ..models import Experiment, Team
from ..config import MIN_ALLOWED_TEAMS, MAX_ALLOWED_TEAMS


def get_experiments(db: Session, team_name: str | None, limit: int | None):
    query = (
        db.query(Experiment)
        .join(Experiment.teams)
        .options(
            joinedload(Experiment.teams)
            .load_only(Team.id, Team.name)
        )
        .order_by(asc(Experiment.description))
    )
    
    if team_name:
        filtered_team = db.query(Team).filter(Team.name == team_name).first()
        if not filtered_team:
            raise HTTPException(status_code=404, detail=TEAM_BY_NAME_NOT_FOUND_ERROR)

        query = query.filter(
            or_(
                Team.id == filtered_team.id,
                Team.parent_team == filtered_team.id
            )
        )        
    
    return query.limit(limit).all()


def create_experiment(db: Session, description: str, sample_ratio: float, allowed_team_assignments: int, team_ids: list[uuid.UUID]):
    check_allowed_team_assignment_value(allowed_team_assignments)
    
    team_ids_set = set({str(team) for team in team_ids})
    check_team_assignments_amount(allowed_team_assignments, team_ids_set)

    existing_teams = db.query(Team).filter(Team.id.in_(team_ids_set)).all()
    existing_teams_ids_set = set({str(team.id) for team in existing_teams})
    check_if_teams_exist(team_ids_set, existing_teams_ids_set)

    check_parent_child_relationship_in_assignment(existing_teams, existing_teams_ids_set)
    
    db_experiment = Experiment(
        id=str(uuid.uuid4()),
        description=description,
        sample_ratio=sample_ratio,
        allowed_team_assignments=allowed_team_assignments
    )
    db.add(db_experiment)

    for team in existing_teams:    
        db_experiment.teams.append(team)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=UNEXPECTED_ERROR)
    
    db.refresh(db_experiment)

    return {
        "message": EXPERIMENT_CREATED_SUCCESSFULLY_MSG,
        "experiment_id": str(db_experiment.id),
    }


def update_assignments(db: Session, experiment_id: str, team_ids: list[str]):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    check_if_experiment_exists(experiment)
    
    team_ids_set = set(team_ids)
    check_team_assignments_amount(experiment.allowed_team_assignments, team_ids_set)

    existing_teams = db.query(Team).filter(Team.id.in_(team_ids_set)).all()
    existing_teams_ids_set = set({str(team.id) for team in existing_teams})
    check_if_teams_exist(team_ids_set, existing_teams_ids_set)

    current_assigned_teams = set({str(team.id) for team in experiment.teams})
    check_if_assignments_exist(current_assigned_teams, team_ids_set)
    
    check_parent_child_relationship_in_assignment(existing_teams, existing_teams_ids_set)
    
    set_to_assign = set(team_ids) - current_assigned_teams
    teams_to_assign = db.query(Team).filter(Team.id.in_(set_to_assign)).all()
    set_to_unasign = current_assigned_teams - set(team_ids)
    teams_to_unassign = db.query(Team).filter(Team.id.in_(set_to_unasign)).all()

    for team in teams_to_assign:
        experiment.teams.append(team)
    
    for team in teams_to_unassign:
        experiment.teams.remove(team)
            
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=UNEXPECTED_ERROR)
    
    return {"message": ASSIGNMENTS_UPDATED_MSG}


def check_allowed_team_assignment_value(allowed_team_assignments: int):
    if not (MIN_ALLOWED_TEAMS <= allowed_team_assignments <= MAX_ALLOWED_TEAMS):
            raise HTTPException(
                status_code=400, 
                detail=VALUE_OF_ALLOWED_TEAM_ASSIGNMNETS_RANGE_ERROR.format(
                    min=MIN_ALLOWED_TEAMS, max=MAX_ALLOWED_TEAMS
                )
            )
    

def check_team_assignments_amount(allowed_team_assignments: int, team_ids: set):
    if allowed_team_assignments != len(team_ids):
        raise HTTPException(
            status_code=400, 
            detail=INVALID_ASSIGNMENTS_AMOUNT.format(
                allowed_assignments=allowed_team_assignments
            )
        )


def check_if_teams_exist(passed_team_ids: set[str], existing_teams_ids: set[str]):
    if len(existing_teams_ids) != len(passed_team_ids):
        not_found_teams_ids = passed_team_ids - existing_teams_ids
        raise HTTPException(
            status_code=404,
            detail=TEAMS_NOT_FOUND.format(ids=not_found_teams_ids)
            )


def  check_parent_child_relationship_in_assignment(teams: list[Team], teams_ids: set[str]):
    for team in teams:
        if str(team.parent_team) in teams_ids:
            raise HTTPException(
                status_code=400, 
                detail=CANNOT_ASSIGN_CHILD_WITH_PARENT_TO_EXPERIMENT_ERROR
            )


def check_if_experiment_exists(experiment: Experiment):
    if not experiment:
        raise HTTPException(status_code=404, detail=EXPERIMENT_NOT_FOUND_ERROR)


def check_if_assignments_exist(current_assigned_teams: set[str], team_ids: set[str]):
    if current_assigned_teams == team_ids:
        raise HTTPException(status_code=400, detail=ASSIGNMENTS_ALREADY_EXISTS_ERROR)

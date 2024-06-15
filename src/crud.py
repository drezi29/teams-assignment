from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session
import uuid

from . import messages, models
from .config import MIN_ALLOWED_TEAMS, MAX_ALLOWED_TEAMS


def get_experiments(team_name: str | None, limit: int | None, db: Session):
    query = (
        db.query(models.Experiment)
        .join(models.Experiment.teams)
        .options(
            joinedload(models.Experiment.teams)
            .load_only(models.Team.id, models.Team.name)
        )
    )
    
    if team_name:
        filtered_team = db.query(models.Team).filter(models.Team.name == team_name).first()
        if not filtered_team:
            raise HTTPException(status_code=404, detail=messages.TEAM_BY_NAME_NOT_FOUND_ERROR)

        query = query.filter(
            or_(
                models.Team.id == filtered_team.id,
                models.Team.parent_team == filtered_team.id
            )
        )        
    
    return query.limit(limit).all()


def create_experiment(db: Session, description: str, sample_ratio: float, allowed_team_assignments: int, team_ids: list[str]):
    if not (MIN_ALLOWED_TEAMS <= allowed_team_assignments <= MAX_ALLOWED_TEAMS):
        raise HTTPException(
            status_code=400, 
            detail=messages.VALUE_OF_ALLOWED_TEAM_ASSIGNMNETS_RANGE_ERROR.format(
                min=MIN_ALLOWED_TEAMS, max=MAX_ALLOWED_TEAMS
            )
        )
    
    db_experiment = models.Experiment(
        id=str(uuid.uuid4()),
        description=description,
        sample_ratio=sample_ratio,
        allowed_team_assignments=allowed_team_assignments
    )
    db.add(db_experiment)

    set_team_ids = set(team_ids)
    if allowed_team_assignments != len(set_team_ids):
        raise HTTPException(status_code=400, detail=f"That experiment requires {allowed_team_assignments} team(s) to assign")

    teams = db.query(models.Team).filter(models.Team.id.in_(set_team_ids)).all()
    set_teams_ids_str = set({str(team.id) for team in teams})
    if len(teams) != len(set_team_ids):
        not_found_teams_ids = set_team_ids - set_teams_ids_str
        raise HTTPException(status_code=404, detail=f"Team(s) not found: {not_found_teams_ids}")

    for team in teams:
        if str(team.parent_team) in set_teams_ids_str:
            raise HTTPException(status_code=404, detail=f"Cannot assign a child of the team to the same experiment")
    
    for team in teams:    
        db_experiment.teams.append(team)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    
    db.refresh(db_experiment)
    return db_experiment


def update_assignments(db: Session, experiment_id: str, team_ids: list[str]):
    experiment = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    set_team_ids = set(team_ids)
    allowed_team_assignments = experiment.allowed_team_assignments
    if allowed_team_assignments != len(set_team_ids):
        raise HTTPException(status_code=400, detail=f"That experiment requires {allowed_team_assignments} team(s) to assign")

    teams = db.query(models.Team).filter(models.Team.id.in_(set_team_ids)).all()
    set_teams_ids_str = set({str(team.id) for team in teams})
    if len(teams) != len(set_team_ids):
        not_found_teams_ids = set_team_ids - set_teams_ids_str
        raise HTTPException(status_code=404, detail=f"Team(s) not found: {not_found_teams_ids}")

    current_assigned_teams = set({str(team.id) for team in experiment.teams})
    if current_assigned_teams == set(team_ids):
        raise HTTPException(status_code=400, detail=f"Assignment exists")
    
    for team in teams:
        if str(team.parent_team) in set_teams_ids_str:
            raise HTTPException(status_code=404, detail=f"Cannot assign a child of the team to the same experiment")
    
    set_to_assign = set(team_ids) - current_assigned_teams
    teams_to_assign = db.query(models.Team).filter(models.Team.id.in_(set_to_assign)).all()
    set_to_unasign = current_assigned_teams - set(team_ids)
    teams_to_unassign = db.query(models.Team).filter(models.Team.id.in_(set_to_unasign)).all()

    for team in teams_to_assign:
        experiment.teams.append(team)
    
    for team in teams_to_unassign:
        experiment.teams.remove(team)
            
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    
    return {"message": "Assignment updated successfully!"}

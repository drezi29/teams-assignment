from fastapi import Body, Depends, FastAPI, Response, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
from uuid import UUID

from . import crud, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/experiments/")
def read_experiments(
    response: Response,
    team_name: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    
    experiments = crud.get_experiments(team_name, limit, db)
    if not experiments:
        response.status_code = status.HTTP_204_NO_CONTENT
        return []
    return experiments


@app.post("/experiments/")
def create_experiment(
    description: str = Body(...),
    sample_ratio: float = Body(...),
    allowed_team_assignments: int = Body(...),
    team_ids: List[UUID] = Body(...),
    db: Session = Depends(get_db)
):
    
    return crud.create_experiment(db, description, sample_ratio, allowed_team_assignments, team_ids)


@app.put("/experiments/{experiment_id}/teams")
def update_assignments(experiment_id: str, team_ids: Annotated[list[str], Query()], db: Session = Depends(get_db)):
    return crud.update_assignments(db, experiment_id, team_ids)


@app.get("/teams/")
def read_teams(
    response: Response,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    
    teams = crud.get_teams(limit, db)
    if not teams:
        response.status_code = status.HTTP_204_NO_CONTENT
        return []
    return teams


@app.post("/teams/")
def create_team(
    name: str = Body(...),
    parent_team_id: UUID | None = Body(None),
    db: Session = Depends(get_db)
):

    team = crud.create_team(db, name, parent_team_id)
    return team

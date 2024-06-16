from typing import Annotated, List
from uuid import UUID

from fastapi import Body, Depends, FastAPI, Query, Response, status
from sqlalchemy.orm import Session

from . import crud, models
from .crud.experiment import create_experiment, get_experiments, update_assignments
from .crud.team import create_team, get_teams
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
    db: Session = Depends(get_db),
):
    experiments = crud.experiment.get_experiments(db, team_name, limit)
    if not experiments:
        response.status_code = status.HTTP_204_NO_CONTENT
        return []
    return experiments


@app.post("/experiments/")
def create_experiment(
    response: Response,
    description: str = Body(...),
    sample_ratio: float = Body(...),
    allowed_team_assignments: int = Body(...),
    team_ids: List[UUID] = Body(...),
    db: Session = Depends(get_db),
):
    experiment = crud.experiment.create_experiment(
        db, description, sample_ratio, allowed_team_assignments, team_ids
    )
    response.status_code = status.HTTP_201_CREATED
    return experiment


@app.put("/experiments/{experiment_id}/teams")
def update_assignments(
    experiment_id: str,
    team_ids: Annotated[list[str], Query()],
    db: Session = Depends(get_db),
):
    return crud.experiment.update_assignments(db, experiment_id, team_ids)


@app.get("/teams/")
def read_teams(response: Response, limit: int = 100, db: Session = Depends(get_db)):
    teams = crud.team.get_teams(db, limit)
    if not teams:
        response.status_code = status.HTTP_204_NO_CONTENT
        return []
    return teams


@app.post("/teams/")
def create_team(
    response: Response,
    name: str = Body(...),
    parent_team_id: UUID | None = Body(None),
    db: Session = Depends(get_db),
):
    team = crud.team.create_team(db, name, parent_team_id)
    response.status_code = status.HTTP_201_CREATED
    return team


@app.get("/")
async def read_main():
    return {"message": "Team assignments app"}

from fastapi import Depends, FastAPI, Response, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from .database import SessionLocal, engine
from . import crud, models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/experiments/")
def read_experiments(response: Response, team_name: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    experiments = crud.get_experiments(db, team_name, limit)
    if not experiments:
        response.status_code = status.HTTP_204_NO_CONTENT
    return experiments

@app.post("/experiments/")
def create_experiment(description: str, sample_ratio: float, allowed_team_assignments: int, team_ids: Annotated[list[str], Query()], db: Session = Depends(get_db)):
    return crud.create_experiment(db, description, sample_ratio, allowed_team_assignments, team_ids)

@app.put("/experiments/{experiment_id}/teams")
def update_assignments(experiment_id: str, team_ids: Annotated[list[str], Query()], db: Session = Depends(get_db)):
    return crud.update_assignments(db, experiment_id, team_ids)
    
@app.get("/teams/")
def read_teams(response: Response, limit: int = 100, db: Session = Depends(get_db)):
    teams = crud.get_teams(db, limit)
    if not teams:
        response.status_code = status.HTTP_204_NO_CONTENT
    return teams

@app.post("/teams/")
def create_team(name: str, db: Session = Depends(get_db)):
    team = crud.create_team(db, name)
    return team








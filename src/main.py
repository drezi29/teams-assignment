from fastapi import Depends, FastAPI, Response, status, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud, models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/experiments/")
def create_experiment(description: str, sample_ratio: float, allowed_team_assignments: int, db: Session = Depends(get_db)):
    experiment = crud.create_experiment(db, description, sample_ratio, allowed_team_assignments)
    return experiment


@app.get("/experiments/")
def read_experiments(response: Response, limit: int = 100, db: Session = Depends(get_db)):
    experiments = crud.get_experiments(db, limit=limit)
    if not experiments:
        response.status_code = status.HTTP_204_NO_CONTENT
    return experiments

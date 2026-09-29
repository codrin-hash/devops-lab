import uuid

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schemas import AppCreate, AppOut
from common.db import Base, engine, get_session
from common.models import App

app = FastAPI(title="idp")


@app.on_event("startup")
def init_db() -> None:
    # Datorie tehnica: create_all nu face migrari. Alembic vine cand schema se schimba.
    Base.metadata.create_all(engine)


@app.get("/healthz")
def healthz(response: Response, db: Session = Depends(get_session)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        response.status_code = 503
        return {"status": "db_unavailable"}


@app.post("/apps", response_model=AppOut, status_code=201)
def create_app(body: AppCreate, db: Session = Depends(get_session)):
    obj = App(name=body.name, repo_url=str(body.repo_url), branch=body.branch)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, f"app '{body.name}' already exists")
    return obj


@app.get("/apps", response_model=list[AppOut])
def list_apps(db: Session = Depends(get_session)):
    return db.scalars(select(App).order_by(App.created_at)).all()


@app.get("/apps/{app_id}", response_model=AppOut)
def get_app(app_id: uuid.UUID, db: Session = Depends(get_session)):
    obj = db.get(App, app_id)
    if obj is None:
        raise HTTPException(404, "app not found")
    return obj
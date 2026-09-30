import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schemas import AppCreate, AppOut, DeploymentOut
from common.db import Base, engine, get_session
from common.models import App, Deployment
from common.queue import enqueue

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # TD-002: no migrations yet
    yield

app = FastAPI(title="idp")

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

@app.post("/apps/{app_id}/deploys", response_model=DeploymentOut, status_code=202)
def create_deploy(app_id: uuid.UUID, session: Session = Depends(get_session)):
    if session.get(App, app_id) is None:
        raise HTTPException(404, "app not found")
    dep = Deployment(app_id=app_id)
    session.add(dep)
    session.commit()
    session.refresh(dep)
    enqueue(str(dep.id))
    return dep

@app.get("/apps/{app_id}/deploys", response_model=list[DeploymentOut])
def list_deploys(app_id: uuid.UUID, session: Session = Depends(get_session)):
    if session.get(App, app_id) is None:
        raise HTTPException(404, "app not found")
    stmt = select(Deployment).where(Deployment.app_id == app_id).order_by(Deployment.created_at.desc())
    return session.scalars(stmt).all()

@app.get("/deploys/{deploy_id}", response_model=DeploymentOut)
def get_deploy(deploy_id: uuid.UUID, session: Session = Depends(get_session)):
    dep = session.get(Deployment, deploy_id)
    if dep is None:
        raise HTTPException(404, "deployment not found")
    return dep
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from common.db import Base


class DeployStatus(str, enum.Enum):
    queued = "queued"
    cloning = "cloning"
    building = "building"
    starting = "starting"
    running = "running"
    failed = "failed"


class App(Base):
    __tablename__ = "apps"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    repo_url: Mapped[str] = mapped_column(Text)
    branch: Mapped[str] = mapped_column(String(255), default="main")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    app_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("apps.id", ondelete="CASCADE"), index=True)
    status: Mapped[DeployStatus] = mapped_column(Enum(DeployStatus, name="deploy_status"), default=DeployStatus.queued)
    commit_sha: Mapped[str | None] = mapped_column(String(40))
    image: Mapped[str | None] = mapped_column(Text)
    container_id: Mapped[str | None] = mapped_column(String(64))
    host_port: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from common.models import DeployStatus

NAME_RE = r"^[a-z][a-z0-9-]{1,30}[a-z0-9]$"  # DNS label, <= 32 caractere


class AppCreate(BaseModel):
    name: str = Field(pattern=NAME_RE)
    repo_url: HttpUrl
    branch: str = Field(default="main", min_length=1, max_length=255)

    @field_validator("repo_url")
    @classmethod
    def https_only(cls, v: HttpUrl) -> HttpUrl:
        if v.scheme != "https":
            raise ValueError("only https:// repositories are allowed")
        return v


class AppOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    repo_url: str
    branch: str
    created_at: datetime

class DeploymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    app_id: uuid.UUID
    status: DeployStatus
    commit_sha: str | None
    image: str | None
    host_port: int | None
    error: str | None
    created_at: datetime
    updated_at: datetime
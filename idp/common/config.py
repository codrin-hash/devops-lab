from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://idp:idp@postgres:5432/idp"
    redis_url: str = "redis://redis:6379/0"
    workspace_dir: str = "/workspace"


settings = Settings()
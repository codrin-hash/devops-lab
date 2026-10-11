from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://idp:idp@postgres:5432/idp"
    redis_url: str = "redis://redis:6379/0"
    workspace_dir: str = "/workspace"
    apps_network: str = "idp-apps"
    app_port: int = 8000
    build_timeout: int = 600
    health_timeout: int = 60
    app_mem_limit: str = "256m"
    app_nano_cpus: int = 500_000_000  # 0.5 CPU
    app_pids_limit: int = 256


settings = Settings()
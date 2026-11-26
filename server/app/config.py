from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/tickets"
    redis_url: str = "redis://localhost:6379/0"
    processing_delay_min: float = 2.0
    processing_delay_max: float = 5.0

    worker_force_error: bool = False


settings = Settings()
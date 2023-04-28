from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_DSN: str
    MIN_POOL_SIZE: int = 3
    MAX_POOL_SIZE: int = 10

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_DSN: str
    MIN_POOL_SIZE: int = 3
    MAX_POOL_SIZE: int = 10

    DEBUG_LEVEL: str = "DEBUG"

    POINT_MARKET_DICTIONARY: str
    POINT_HANDBOOK: str


    class Config:
        env_file = ".env"


settings = Settings(_env_file=r'C:\projects\moex_fast_utils\.env')

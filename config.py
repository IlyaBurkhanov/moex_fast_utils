import asyncio
from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG_LEVEL: str = "DEBUG"
    MAX_PROCESS: int = 4
    MAX_ASYNC_REQUEST_WORKER: int = 5

    # DB
    DB_DSN: str
    MIN_POOL_SIZE: int = 3
    MAX_POOL_SIZE: int = 10
    MIN_POOL_SIZE_PROCESS: int = 2
    MAX_POOL_SIZE_PROCESS: int = 5

    # POINTS
    POINT_MARKET_DICTIONARY: str
    POINT_HANDBOOK: str
    POINT_SECURITY_INFO: str
    POINT_SECURITY_DAY_HISTORY: str

    # QUERY
    QUEUE_THREAD_MAX_SIZE: int = 10_000
    QUEUE_PROCESS_MAX_SIZE: int = 200

    class Config:
        env_file = ".env"


settings = Settings(_env_file=r'C:\projects\moex_fast_utils\.env')

QUEUE_THREAD = asyncio.Queue(maxsize=settings.QUEUE_THREAD_MAX_SIZE)
QUEUE_PROCESS = asyncio.Queue(maxsize=settings.QUEUE_PROCESS_MAX_SIZE)
REQUEST_SEMAPHORE = asyncio.Semaphore(settings.MAX_ASYNC_REQUEST_WORKER)  # USE FOR HISTORY DATA

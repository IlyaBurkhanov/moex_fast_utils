import asyncpg
from asyncpg.pool import Pool
from config import settings
from utils import singleton


@singleton
class DataBase:
    _pool: Pool = None

    async def create_pool(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                dsn=settings.DB_DSN,
                min_size=settings.MIN_POOL_SIZE,
                max_size=settings.MAX_POOL_SIZE,
            )

    @property
    def pool(self):
        return self._pool


moex_db = DataBase()

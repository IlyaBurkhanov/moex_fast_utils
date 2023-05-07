import asyncio

import asyncpg
from asyncpg.pool import Pool
from contextlib import asynccontextmanager
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

    def __del__(self):
        try:
            if self.pool:
                asyncio.get_running_loop().run_until_complete(self._pool.close())
        except Exception:
            pass

@asynccontextmanager
async def pool_for_process():
    pool = await asyncpg.create_pool(
        dsn=settings.DB_DSN,
        min_size=settings.MIN_POOL_SIZE_PROCESS,
        max_size=settings.MAX_POOL_SIZE_PROCESS
    )
    try:
        yield pool
    finally:
        await pool.close()


MOEX_DB = DataBase()

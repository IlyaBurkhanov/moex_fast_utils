from db import MOEX_DB


async def async_executor(sql_raw):
    async with MOEX_DB.pool.acquire() as connection:
        return await connection.execute(sql_raw)

from db import moex_db


async def async_executor(sql_raw):
    async with moex_db.pool.acquire() as connection:
        return await connection.execute(sql_raw)

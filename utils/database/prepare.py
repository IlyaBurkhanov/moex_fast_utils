import aiohttp
import asyncio
import sys
from loguru import logger

from db import moex_db
from migrations import market_types
from config import settings

sql_all_tables = """
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
"""


def exit_if_error(_):
    sys.exit(-1)


@logger.catch(onerror=exit_if_error)
async def prepare_database():
    async with moex_db.pool.acquire() as connection:
        tables = set(dict(table)["table_name"] for table in await connection.fetch(sql_all_tables))
        for table in market_types.create_table_order:
            if table not in tables:
                await connection.execute(getattr(market_types, table))


async def save_dictionaries_in_db(table_name: str, data: dict) -> None:
    sql_template = f"""
        INSERT INTO {table_name}({', '.join(data['columns'])}) 
        VALUES({', '.join(['$' + str(number) for number in range(1, len(data['columns']) + 1)])}) 
        ON CONFLICT DO NOTHING;
    """
    async with moex_db.pool.acquire() as connection:
        await connection.executemany(sql_template, data["data"])


@logger.catch(onerror=exit_if_error)
async def get_dictionaries_from_moex():
    async with aiohttp.ClientSession() as client:
        handbook_dict, index_dict = await asyncio.gather(
            client.get(settings.POINT_HANDBOOK),
            client.get(settings.POINT_MARKET_DICTIONARY)
        )
        handbook, index_data = await asyncio.gather(handbook_dict.json(), index_dict.json())
        handbook_data = handbook["handbooks_handbook"]
        await save_dictionaries_in_db("handbook", handbook_data)

        for table_ord_inx in range(1, len(market_types.create_table_order)):
            table = market_types.create_table_order[table_ord_inx]
            await save_dictionaries_in_db(table, index_data[table])

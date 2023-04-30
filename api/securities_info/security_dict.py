import asyncio
from typing import Literal

import aiohttp
from loguru import logger
from datetime import date, datetime
from fastapi import APIRouter, Query
from pydantic import BaseModel, validator
from starlette import status
from starlette.responses import JSONResponse

from config import settings
from db import moex_db
from sql_requests.security_info import (
    GET_SECID_INFO,
    INSERT_INTO_SECURITY,
    SECURITY_COLUMNS,
)

router_security_dict = APIRouter()

BOARDS_COLUMNS = ["boardid", "market", "engine", "is_traded", "is_primary", "currencyid"]
BOARDS_COLUMNS_SET = set(BOARDS_COLUMNS)
COLUMN_WITH_DATE = {"history_from", "history_till", "listed_from", "listed_till"}
SQL_SECURITY_BOARDS = (
    "SELECT %s FROM security_boards WHERE secid=$1 ORDER BY is_primary desc, is_traded desc"
    % ", ".join(BOARDS_COLUMNS)
)


class SecurityInfo(BaseModel):
    SECID: str
    NAME: str | None
    SHORTNAME: str | None
    ISIN: str | None
    REGNUMBER: str | None
    ISSUESIZE: int | None
    FACEVALUE: float | None
    FACEUNIT: str | None
    ISSUEDATE: date | None
    LATNAME: str | None
    LISTLEVEL: int | None
    ISQUALIFIEDINVESTORS: int | None
    TYPENAME: str | None
    GROUP: str | None
    TYPE: str | None
    GROUPNAME: str | None
    EMITTER_ID: str | None

    @validator("FACEVALUE")
    def result_check(cls, v):
        if v:
            return round(v, 8)


@logger.catch
async def security_from_db(attribute, value):
    async with moex_db.pool.acquire() as connection:
        result = await connection.fetchrow(GET_SECID_INFO % attribute, value)
        if result:
            return {key.upper(): value for key, value in dict(result).items()}


@logger.catch
async def get_security_by_api(secid: str):
    async with aiohttp.ClientSession() as client:
        request = await client.get(settings.POINT_SECURITY_INFO + secid + ".json")
        return await request.json()


def get_security_model(data: dict):
    """Get dictionary by key 'description' from moex api data"""
    return SecurityInfo(**{value[0].upper(): value[2] for value in data["data"]})


@logger.catch
async def save_security(model: SecurityInfo):
    result = model.dict()
    values = [result[column] for column in SECURITY_COLUMNS]
    async with moex_db.pool.acquire() as connect:
        await connect.execute(INSERT_INTO_SECURITY, *values)


@logger.catch
async def save_security_boards(data: dict):
    """Get dictionary by key 'boards' from moex api data"""
    raw_sql = 'INSERT INTO security_boards (%s) VALUES (%s) ON CONFLICT DO NOTHING' % (
        ', '.join([f'"{column}"' for column in data["columns"]]),
        ', '.join([f"${pos}" for pos in range(1, len(data["columns"]) + 1)]),
    )

    date_position = [num for num, column in enumerate(data["columns"]) if column in COLUMN_WITH_DATE]
    for values in data["data"]:
        for num in date_position:
            if values[num]:
                values[num] = datetime.strptime(values[num], "%Y-%m-%d").date()

    async with moex_db.pool.acquire() as connect:
        await connect.executemany(raw_sql, data["data"])


async def save_all_result(data: dict, model: SecurityInfo | None = None):
    """data - json from moex api"""
    if not model:
        model = get_security_model(data["description"])
    tasks = [asyncio.create_task(save_security(model))]
    if "boards" in data and data["boards"].get("data"):
        tasks.append(asyncio.create_task(save_security_boards(data["boards"])))
    await asyncio.gather(*tasks)


@router_security_dict.get("/{security_id}", description="Get info about security", tags=["security"])
async def get_secid(
        security_id: str,
        attribute: Literal["secid", "isin"] = Query(
            default="secid",
            description="Data from MOEX-api are possible only by 'secid'!"
        ),
):
    if result := await security_from_db(attribute, security_id):
        return result

    if attribute != "isin":
        result_api = await get_security_by_api(security_id)
        if result_api["description"].get("data"):
            model = get_security_model(result_api["description"])
            asyncio.create_task(save_all_result(result_api, model))
            return model
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"details": "Security is not found!"})


@router_security_dict.get("/boards/{security_id}", description="Get boards by security", tags=["security"])
async def get_boards_by_secid(
        security_id: str,
):
    async with moex_db.pool.acquire() as connect:
        if boards_db := await connect.fetch(SQL_SECURITY_BOARDS, security_id):
            values = []
            for board in boards_db:
                board_dict = dict(board)
                values.append([board_dict[column] for column in BOARDS_COLUMNS])
            return {
                "columns": BOARDS_COLUMNS,
                "values": values,
            }
        data_api, data_db = await asyncio.gather(
            get_security_by_api(security_id),
            connect.fetchrow("SELECT secid FROM security_description WHERE secid=$1", security_id),
        )
        if not data_api.get("description", {}).get("data"):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"details": "Security is not found!"})

        if not data_db:
            asyncio.create_task(save_all_result(data_api))
        elif data_api.get("boards", {}).get("data"):
            asyncio.create_task(save_security_boards(data_api["boards"]))
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"details": f"Boards for {security_id} is not found!"}
            )
        column_position = [
            (num, column) for num, column in enumerate(data_api["boards"]["columns"]) if column in BOARDS_COLUMNS_SET
        ]
        values = [[board_values[num] for num, _ in column_position] for board_values in data_api["boards"]["data"]]
        return {
            "columns": [column for _, column in column_position],
            "values": values
        }


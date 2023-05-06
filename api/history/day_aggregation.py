import asyncio

from asyncpg import PostgresError
import aiohttp
from loguru import logger
from datetime import date, datetime
from db import MOEX_DB
from config import settings, REQUEST_SEMAPHORE
from fastapi import APIRouter, HTTPException
from pydantic import root_validator
from sql_requests.log_session_history import raw_sql_get_requests_to_api_history
from utils.validators.secid_and_market import DefaultValidateDataModel, check_default_values

router_security_history = APIRouter()


class SecurityDayHistoryModel(
    DefaultValidateDataModel,
    use_required_fields={"engine", "market", "session", "secid"},
    use_optional_fields={},
):
    start_date: date
    end_date: date

    @root_validator
    def check_date_period(cls, values):
        end_date, start_date = values.get("end_date"),  values.get("start_date")
        if end_date < start_date:
            raise HTTPException(status_code=400, detail=f"Last Date > First date")
        if start_date < date(2015, 1, 1):
            raise HTTPException(status_code=400, detail=f"Date can be more then 2014-12-31")
        if (end_date - start_date).days >= 367:
            raise HTTPException(status_code=400, detail=f"Not more then 366 days")
        return values


class WorkWithDayHistory:
    LOG_ATTRIBUTES_ORDER = ["secid", "engine", "market", "session", "start_date", "end_date"]
    SQL_INSERT_LOG = """
        INSERT INTO logs_session_security_history (start_date, end_date, engine, market, session, secid, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id;
    """

    def __init__(self, request: SecurityDayHistoryModel):
        self.request = request
        self.wait_id_request = set()
        self.url_history = settings.POINT_SECURITY_DAY_HISTORY.format(**dict(request))
        self.wait_save_id = []
        self.session: aiohttp.ClientSession | None = None

    def __del__(self):
        if self.session:
            try:
                asyncio.get_running_loop().create_task(self.session.close())
            except Exception:
                pass

    async def save_wait_transaction(self, start_date: date, end_date: date):
        async with MOEX_DB.pool.acquire() as connection:
            try:
                wait_id = await connection.fethcval(
                    self.SQL_INSERT_LOG,
                    *[
                        start_date,
                        end_date,
                        self.request.engine,
                        self.request.market,
                        self.request.session,
                        self.request.secid,
                        'wait',
                    ],
                )
                self.wait_id_request.add(wait_id)
                return wait_id
            except PostgresError as err:
                text = f"Save await request from api '{self.request.secid}: {start_date} - {end_date}'. ERROR: " + "{}"
                logger.error(text, err)
                raise HTTPException(status_code=500, detail=err.as_dict())

    async def history_from_api(self, start_date: str, end_date: str, start: int, only_data: bool = True):
        params = {"from": start_date, "till": end_date, "start": start}
        with logger.catch(reraise=True):
            async with REQUEST_SEMAPHORE:
                async with self.session.get(self.url_history, params=params) as request:
                    status = request.status
                    if not (200 <= status < 300):
                        raise HTTPException(
                            status_code=status,
                            detail=f"History {start_date} - {end_date} by secid [{self.request.secid}] "
                                   f"return status - {status}"
                        )
                    result = await request.json()
            if only_data:
                return result["history"]["data"]
            return result



    async def history(self, start_date: date, end_date: date):
        wait_id = await self.save_wait_transaction(start_date, end_date)
        start_date_str, end_date_str = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        first_request = await self.history_from_api(start_date_str, end_date_str, start=0, only_data=False)
        final_data = []
        columns = first_request["history"]["columns"]
        trade_date_index = columns.index("TRADEDATE")
        history_cursor = first_request["history.cursor"]["data"] if not final_data else None
        if not first_request["history"]["data"]:
            #



    async def get_history_from_api(self):
        request_value = [getattr(self.request, column) for column in self.LOG_ATTRIBUTES_ORDER]
        async with MOEX_DB.pool.acquire() as connect:
            result = [dict(row) for row in await connect.fetch(raw_sql_get_requests_to_api_history, *request_value)]

        self.wait_id_request = [data["id"] for data in result if data["wait_status"]]
        if not result:
            print("Идем в базу")
        self.session = aiohttp.ClientSession()

        return result


@router_security_history.post("/security_by_days", tags=["Days History"])
async def get_days_history(data: SecurityDayHistoryModel):
    await check_default_values(data)
    try:
        return await get_history_from_api(data)
    except Exception as error:
        # ДРОП ВСЕ ЗАДАЧИ с ожиданием
        raise error
    # return {'a': "b"}

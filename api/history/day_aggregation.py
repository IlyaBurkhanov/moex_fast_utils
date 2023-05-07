import asyncio

from asyncpg import PostgresError
import aiohttp
from loguru import logger
from datetime import date, datetime, timedelta
from db import MOEX_DB
from config import settings, REQUEST_SEMAPHORE
from fastapi import APIRouter, HTTPException
from pydantic import root_validator, validator
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
        if (end_date - start_date).days >= 3000:
            raise HTTPException(status_code=400, detail=f"Not more then 3000 days")
        return values

    @validator("end_date")
    def check_end_date(cls, v):
        if v >= (last_date := datetime.now().date() - timedelta(days=1)):
            return last_date
        return v


class WorkWithDayHistory:
    TRADE_DATE_COLUMN = "TRADEDATE"
    CURSOR_INDEX_COLUMN = "INDEX"
    CURSOR_TOTAL_COLUMN = "TOTAL"
    CURSOR_SIZE_COLUMN = "PAGESIZE"
    LOG_ATTRIBUTES_ORDER = ["secid", "engine", "market", "session", "start_date", "end_date"]
    SQL_INSERT_LOG = """
        INSERT INTO logs_session_security_history (start_date, end_date, engine, market, session, secid, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id;
    """
    SQL_DELETE_LOG_TRANSACTION = """
        DELETE FROM logs_session_security_history WHERE id=$1
    """
    SQL_INSERT_HISTORY = """
        INSERT INTO session_security_history (%s) values (%s) ON CONFLICT DO NOTHING;
    """
    SQL_UPDATE_WAIT_REQUEST = """
        UPDATE logs_session_security_history SET status='success' WHERE id=$1
    """
    SQL_CHECK_WAIT_REQUESTS = """
        SELECT id, status FROM logs_session_security_history WHERE id in (%s)
    """
    SQL_GET_RESULT = """
        SELECT boardid,
            tradedate,
            shortname,
            secid,
            numtrades,
            value,
            open,
            low,
            high,
            legalcloseprice,
            waprice,
            close,
            volume,
            marketprice2,
            marketprice3,
            admittedquote,
            mp2valtrd,
            marketprice3tradesvalue,
            admittedvalue,
            waval,
            tradingsession 
        FROM session_security_history
        WHERE secid=$1
        AND tradedate between $2 AND $3
    """

    DATE_FORMAT = "%Y-%m-%d"

    __slots__ = (
        "request",
        "wait_id_request",
        "url_history",
        "wait_save_id",
        "session",
        "columns",
        "trade_date_index",
        "cursor_columns",
        "cursor_index_idx",
        "cursor_total_idx",
        "cursor_size_idx",
    )

    def __init__(self, request: SecurityDayHistoryModel):
        self.request = request
        self.wait_id_request: set = set()
        self.url_history: str = settings.POINT_SECURITY_DAY_HISTORY.format(**dict(request))
        self.wait_save_id: set = set()
        self.session: aiohttp.ClientSession | None = None
        self.columns: list = []
        self.trade_date_index: int | None = None
        self.cursor_columns: list = []
        self.cursor_index_idx: int | None = None
        self.cursor_total_idx: int | None = None
        self.cursor_size_idx: int | None = None

    def __del__(self):
        if self.session and not self.session.closed:
            try:
                asyncio.get_running_loop().create_task(self.session.close())
            except Exception:
                pass

    async def save_wait_transaction(self, start_date: date, end_date: date) -> int:
        async with MOEX_DB.pool.acquire() as connection:
            try:
                wait_id = await connection.fetchval(
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
                self.wait_save_id.add(wait_id)
                return wait_id
            except PostgresError as err:
                text = f"Save await request from api '{self.request.secid}: {start_date} - {end_date}'. ERROR: " + "{}"
                logger.error(text, err)
                raise HTTPException(status_code=500, detail=err.as_dict())

    async def delete_wait_transaction(self, transaction_id: int):
        async with MOEX_DB.pool.acquire() as connection:
            await connection.execute(self.SQL_DELETE_LOG_TRANSACTION, transaction_id)
        self.wait_save_id.remove(transaction_id)

    def date_str_to_date(self, data):
        for row in data:
            row[self.trade_date_index] = datetime.strptime(row[self.trade_date_index], self.DATE_FORMAT).date()

    async def history_from_api(self, start_date: str, end_date: str, start: int, only_data: bool = True) -> dict | list:
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
            if not self.columns:
                self.columns = result["history"]["columns"]
                self.trade_date_index = self.columns.index(self.TRADE_DATE_COLUMN)
            self.date_str_to_date(result["history"]["data"])
            if only_data:
                return result["history"]["data"]
            return result

    async def save_data(self, wait_id: int, data: list[list]):
        async with MOEX_DB.pool.acquire() as connection:
            transaction = connection.transaction()
            await transaction.start()
            try:
                await connection.execute(self.SQL_UPDATE_WAIT_REQUEST, wait_id)
                if data:
                    await connection.executemany(
                        self.SQL_INSERT_HISTORY % (
                            ', '.join(self.columns),
                            ', '.join([f'${idx}' for idx in range(1, len(self.columns) + 1)])
                        ),
                        data,
                    )
                await transaction.commit()
            except PostgresError as error:
                await transaction.rollback()
                await connection.execute(self.SQL_DELETE_LOG_TRANSACTION, wait_id)
                self.wait_save_id.remove(wait_id)
                await transaction.commit()
                logger.error("SAVE ERROR: {}", error)
                raise HTTPException(status_code=500, detail="SOME PROBLEM WITH SAVE RESULT")

    async def history_api(self, start_date: date, end_date: date):
        wait_id = await self.save_wait_transaction(start_date, end_date)
        start_date_str, end_date_str = start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        first_request = await self.history_from_api(start_date_str, end_date_str, start=0, only_data=False)
        final_data = first_request["history"]["data"]
        if final_data:
            if not self.cursor_columns:
                self.cursor_columns = first_request["history.cursor"]["columns"]
                self.cursor_index_idx = self.cursor_columns.index(self.CURSOR_INDEX_COLUMN)  # FIXME: NOT USE
                self.cursor_total_idx = self.cursor_columns.index(self.CURSOR_TOTAL_COLUMN)
                self.cursor_size_idx = self.cursor_columns.index(self.CURSOR_SIZE_COLUMN)
            cursor = first_request["history.cursor"]["data"][0]
            if cursor[self.cursor_total_idx] > cursor[self.cursor_size_idx]:
                total, step = cursor[self.cursor_total_idx], cursor[self.cursor_size_idx]
                start = step
                tasks = []
                while total > start:
                    tasks.append(asyncio.create_task(self.history_from_api(start_date_str, end_date_str, start=start)))
                    start += step
                for done_task in asyncio.as_completed(tasks):
                    try:
                        final_data.extend(await done_task)
                    except Exception as error:
                        [task.cancel() for task in tasks if not task.done()]
                        if not isinstance(error, HTTPException):
                            logger.error("Catch error for get day history from moex api: {}", error)
                        await self.delete_wait_transaction(wait_id)
                        raise error
        await self.save_data(wait_id, final_data)

    async def get_request_parameters(self) -> list[dict]:
        request_value = [getattr(self.request, column) for column in self.LOG_ATTRIBUTES_ORDER]
        async with MOEX_DB.pool.acquire() as connect:
            return [dict(row) for row in await connect.fetch(raw_sql_get_requests_to_api_history, *request_value)]

    async def get_async_request_to_api(self, params: list[dict]) -> bool:
        request_date = [data["request_date"] for data in params if data["request_date"]]
        if request_date:
            self.session = aiohttp.ClientSession()
            first_error = None
            tasks = [asyncio.create_task(self.history_api(*dates)) for dates in request_date]

            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for task_done in done:
                if task_done.exception() is not None:
                    first_error = task_done
                    break
            if first_error is not None:
                for task_pending in pending:
                    task_pending.cancel()

                await asyncio.gather(
                    *[asyncio.create_task(self.delete_wait_transaction(wait_id)) for wait_id in self.wait_save_id]
                )
                raise first_error.exception()
            return True
        return False

    async def check_waited_requests(self, sleep_time: float):
        await asyncio.sleep(sleep_time)
        async with MOEX_DB.pool.acquire() as connection:
            result = await connection.fetch(self.SQL_CHECK_WAIT_REQUESTS % ', '.join(map(str, self.wait_id_request)))

        if len(result) != len(self.wait_id_request):
            text_error = f"Has error in check status of request by {self.request.secid} " \
                         f"on period {self.request.start_date} - {self.request.end_date}. " \
                         f"FOR {self.request.engine}/{self.request.market}/{self.request.session.name}"
            logger.exception(text_error)
            raise HTTPException(status_code=500, detail=text_error)
        for value in result:
            dict_value = dict(value)
            if dict_value["status"] == "success":
                self.wait_id_request.remove(dict_value["id"])
        if len(self.wait_id_request) == 0:
            return True
        return False

    async def get_result(self):
        async with MOEX_DB.pool.acquire() as connect:
            raw_result = await connect.fetch(
                self.SQL_GET_RESULT,
                self.request.secid,
                self.request.start_date,
                self.request.end_date
            )
        if raw_result:
            columns = list(dict(raw_result[0]).keys())
            data = []
            for row in raw_result:
                tmp_dict = dict(row)
                data.append([tmp_dict[key] for key in columns])
            return {"columns": columns, "data": data}
        return None

    async def get_history_from_api(self):
        params = await self.get_request_parameters()
        self.wait_id_request = {data["id"] for data in params if data["wait_status"]}
        has_request_to_api = await self.get_async_request_to_api(params)

        if self.wait_id_request:
            sleep_time = 0 if has_request_to_api else 0.5
            for _ in range(5):
                if await self.check_waited_requests(sleep_time):
                    break
                sleep_time += 1  # MAX WAIT 15 seconds
            else:
                text_error = f"For day history logs_id: {self.wait_id_request} not return result from moex api."
                logger.exception(text_error)
                raise HTTPException(status_code=500, detail=text_error)

        return await self.get_result()


@router_security_history.post("/security_by_days", tags=["Days History"])
async def get_days_history(data: SecurityDayHistoryModel):
    await check_default_values(data)
    worker = WorkWithDayHistory(data)
    result = await worker.get_history_from_api()
    if result:
        return result
    raise HTTPException(status_code=404, detail="Data not found!")

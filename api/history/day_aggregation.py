import asyncpg
import json
from datetime import date
from db import MOEX_DB
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


async def get_history_from_api(data: SecurityDayHistoryModel):
    request_value = [data.secid, data.engine, data.market, data.session, data.start_date, data.end_date]
    async with MOEX_DB.pool.acquire() as connect:
        result = [dict(value) for value in await connect.fetch(raw_sql_get_requests_to_api_history, *request_value)]

    wait_id_request = [data["id"] for data in result if data["status"]]
    print(wait_id_request)
    if not result:
        print("Идем в базу")

    return result


@router_security_history.post("/security_by_days", tags=["Days History"])
async def get_days_history(data: SecurityDayHistoryModel):
    await check_default_values(data)
    return await get_history_from_api(data)
    # return {'a': "b"}

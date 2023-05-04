from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import root_validator, validator

from utils.validators.secid_and_market import DefaultValidateDataModel, check_default_values

router_security_history = APIRouter()


class SecurityDayHistoryModel(
    DefaultValidateDataModel,
    use_required_fields={"engine", "market", "session", "secid"},
    use_optional_fields={},
):
    from_date: date
    to_date: date

    @root_validator
    def check_date_period(cls, values):
        to_date, from_date = values.get("to_date"),  values.get("from_date")
        if to_date < from_date:
            raise HTTPException(status_code=400, detail=f"Last Date > First date")
        if (to_date - from_date).days > 367:
            raise HTTPException(status_code=400, detail=f"Not more then 366 days")
        return values

    @validator("from_date", "to_date")
    def check_date(cls, value):
        if value < date(2015, 1, 1):
            raise HTTPException(status_code=400, detail=f"Date can be more then 2014-12-31")
        return value


@router_security_history.post("/security_by_days", tags=["Days History"])
async def get_days_history(data: SecurityDayHistoryModel):
    await check_default_values(data)
    return {'a': "b"}

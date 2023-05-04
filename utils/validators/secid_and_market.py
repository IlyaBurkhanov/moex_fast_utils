import asyncio
from asyncio import create_task
from typing import Any
from collections import namedtuple
from enum import IntEnum

from fastapi import HTTPException
from pydantic import BaseModel, Field

from db import MOEX_DB
from api.securities_info.security_dict import api_get_and_save_security


Dictionaries = namedtuple("Dictionaries", ["table", "attribute"])


_SQL_TABLES = {
    # "secid": Dictionaries("security_description", "SECID"),
    "engine": Dictionaries("engines", "name"),
    "market": Dictionaries("markets", "market_name"),
    "board": Dictionaries("boards", "boardid"),
    "board_group": Dictionaries("boards", "boardid"),
    "security_type": Dictionaries("securitytypes", "security_type_name"),
    "security_group": Dictionaries("securitygroups", "name"),
    "security_collection": Dictionaries("securitycollections", "name"),
    "main_board": Dictionaries("handbook", "slug"),
}

SQL_TEMPLATE = "SELECT 1 FROM %s WHERE %s = $1"


class Sessions(IntEnum):
    morning = 0
    main = 1
    evening = 2
    total = 3


class DefaultValidateDataModel(BaseModel):
    secid: str = Field(max_length=150)
    isin: str = Field(max_length=150)
    engine: str = Field(max_length=45)
    market: str = Field(max_length=45)
    board: str = Field(max_length=12)
    board_group: str = Field(max_length=45)
    security_type: str = Field(max_length=93)
    security_group: str = Field(max_length=93)
    security_collection: str = Field(max_length=96)
    main_board: str = Field(max_length=189)
    session: Sessions

    def __init_subclass__(cls, use_required_fields: set, use_optional_fields: set, **kwargs):
        use_fields = use_required_fields.union(use_optional_fields)
        for field in tuple(DefaultValidateDataModel.__fields__.keys()):
            if field not in use_fields:
                cls.__fields__.pop(field)
                cls.__validators__.pop(field, None)

        super().__init_subclass__(**kwargs)
        for field in use_optional_fields:
            cls.__fields__[field].outer_type_ = cls.__fields__[field].outer_type_ | None
            cls.__fields__[field].required = False


async def _check_dictionaries(
        table_name: str,
        attr_name: str,
        value: Any,
        return_exception: bool = True,
):
    async with MOEX_DB.pool.acquire() as connect:
        result = await connect.fetchval(SQL_TEMPLATE % (table_name, attr_name), value)
        if not result:
            if return_exception:
                raise HTTPException(status_code=404, detail=f"Not found value {table_name}.{attr_name}: {value}")
            return False
        return True


async def _check_and_get_secid(security_id: str | None, security_attr: str | None):
    if security_id is None:
        return

    find_in_db = await _check_dictionaries("security_description", security_attr, security_id, return_exception=False)
    if find_in_db:
        return

    if security_attr == "secid":
        await api_get_and_save_security(security_id)
    else:
        raise HTTPException(status_code=404, detail=f"ISIN {security_id} is not found!")


async def check_default_values(data: BaseModel):
    check_data = data.dict(exclude_none=True)
    print(check_data, data)
    secid = check_data.pop("secid", None)
    isin = check_data.pop("isin", None)
    security_id, security_attr = (secid, "secid") if secid else (isin, "isin") if isin else (None, None)
    get_secid_task = create_task(_check_and_get_secid(security_id, security_attr))
    try:
        tasks = []
        if check_data:
            for attr, value in check_data.items():
                if table_args := _SQL_TABLES.get(attr):
                    tasks.append(_check_dictionaries(*table_args, value))

            for finished_task in asyncio.as_completed(tasks):
                await finished_task

        await get_secid_task
    finally:
        [coro.close() for coro in tasks if coro.cr_running]
        get_secid_task.cancel()

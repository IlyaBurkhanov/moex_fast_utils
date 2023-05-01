import asyncio

import uvicorn
from fastapi import FastAPI
import sys
from loguru import logger

from config import settings
from db import MOEX_DB
from api.securities_info.security_dict import router_security_dict
from utils.database.prepare import prepare_database, get_dictionaries_from_moex
from workers import process_workers


logger.remove()
logger.add(
    "app_logs.json",
    format="{time} {level} {message}",
    level=settings.DEBUG_LEVEL,
    rotation="5 MB",
    compression="zip",
    serialize=True,
    enqueue=True,  # use queue for multi: process/threads/async (safely)
)
logger.add(sys.stderr, level="INFO")

app = FastAPI()
app.include_router(router_security_dict, prefix="/security")


@app.on_event("startup")
async def startup_settings():
    await MOEX_DB.create_pool()  # CREATE GLOBAL DB POOL
    await prepare_database()  # CREATE DB IF NOT EXISTS
    await get_dictionaries_from_moex()  # UPDATE DICTIONARIES
    asyncio.create_task(process_workers())


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )

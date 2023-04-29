import uvicorn
from fastapi import FastAPI
import sys
from loguru import logger

from config import settings
from db import moex_db
from utils.database.prepare import prepare_database, get_dictionaries_from_moex

logger.remove()
logger.add(
    "app_logs.json",
    format="{time} {level} {message}",
    level=settings.DEBUG_LEVEL,
    rotation="10 MB",
    compression="zip",
    serialize=True,
)
logger.add(sys.stderr, level="INFO")

app = FastAPI()


@app.on_event("startup")
async def startup_settings():
    await moex_db.create_pool()  # CREATE GLOBAL DB POOL
    await prepare_database()  # CREATE DB IF NOT EXISTS
    await get_dictionaries_from_moex()  # UPDATE DICTIONARIES


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )

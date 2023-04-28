import uvicorn
from fastapi import FastAPI

from db import moex_db

app = FastAPI()


@app.on_event("startup")
async def startup_settings():
    await moex_db.create_pool()
    print(moex_db.get_pool())


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )

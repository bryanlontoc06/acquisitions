import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger

from . import dbModels
from .db.database import Base, engine
from .routers import sample

load_dotenv()
env = os.getenv("APP_ENV", "development")
port = int(os.getenv("APP_PORT", 8000))

logger.add("logs/combined.log", rotation="10 MB", retention="10 days")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    registered_tables = list(Base.metadata.tables.keys())
    logger.info(f"🚀 Initializing models from: {dbModels.__name__}")
    logger.info(f"📦 Tables detected in registry: {registered_tables}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ Database sync complete. Tables are ready!")
    yield
    # Shutdown
    await engine.dispose()
    logger.warning("🛑 Database connection closed. Application shutdown.")


app = FastAPI(lifespan=lifespan)

app.include_router(sample.router, prefix="/v1/sample", tags=["sample"])


if __name__ == "__main__":
    uvicorn.run("src.main:app", port=port, reload=True)

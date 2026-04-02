import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import RequestResponseEndpoint

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity, adjust as needed
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Middleware to add security headers to all responses
@app.middleware("http")
async def add_security_headers(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    logger.info(f"📥 Incoming: {request.method} {request.url.path}")
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    logger.info(f"📤 Outgoing: Status {response.status_code}")
    return response


app.include_router(sample.router, prefix="/v1/sample", tags=["sample"])


if __name__ == "__main__":
    uvicorn.run("src.main:app", port=port, reload=True)

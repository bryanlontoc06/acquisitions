import os
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger.add("logs/combined.log", rotation="10 MB", retention="10 days")

app_env = os.getenv("APP_ENV", "local")
env_file = f".env.{app_env}"
logger.info(f"🔍 Loading environment variables from: {app_env}")
env_path = Path(__file__).resolve().parent.parent / "core/config" / env_file
load_dotenv(dotenv_path=env_path)
app_env = os.getenv("APP_ENV", "local")
raw_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

if raw_password is None:
    raise ValueError("DB_PASSWORD environment variable is not set")
encoded_password = urllib.parse.quote_plus(raw_password)

SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{db_user}:{encoded_password}@{db_host}:4000/{db_name}"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    connect_args={"ssl": True},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

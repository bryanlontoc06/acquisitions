from fastapi import FastAPI

from .routers import sample

app = FastAPI()

app.include_router(sample.router, prefix="/v1/sample", tags=["sample"])

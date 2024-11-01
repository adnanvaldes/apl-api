import os
from contextlib import asynccontextmanager

from typing import Annotated, List

from fastapi import FastAPI

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apl_api.routes import router
from apl_api.parser import load_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists("apl.db"):
        os.remove("apl.db")
    load_data()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(load_data, IntervalTrigger(days=1))
    scheduler.start()
    yield
    if os.path.exists("apl.db"):
        os.remove("apl.db")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.include_router(router)



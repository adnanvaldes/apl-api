import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apl_api.routes import router
from apl_api.parser import update_data, download_markdown
from apl_api.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    download_markdown()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_data, IntervalTrigger(days=settings.update_interval))
    scheduler.start()
    update_data()
    yield
    if os.path.exists(settings.database):
        os.remove(settings.database)
    scheduler.shutdown()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    contact=settings.contact,
    license_info=settings.license_info,
    swagger_ui_parameters=settings.swagger_ui,
    lifespan=lifespan,
)

app.include_router(router)

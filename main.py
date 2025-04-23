from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import select
from routes.ultramarine_routes import ultramarine_routes as ultramarines
from config.config_db import create_db_and_tables, get_session
from routes.utils import generate_random_ultramarines
from models.ultramarines import Ultramarine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Generates and initialize new db and its tables"""
    create_db_and_tables()
    with next(get_session()) as session:
        existing_ultramarines = session.exec(select(Ultramarine)).all()
        if not existing_ultramarines:  # If no Ultramarines exist, generate them
            await generate_random_ultramarines(session)  # This will generate and save random Ultramarines to the DB
    yield


chapter = FastAPI(lifespan=lifespan)

chapter.include_router(ultramarines, prefix="/ultramarines_chapter", tags=["Chapter"])

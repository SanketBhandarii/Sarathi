from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    changes,
    documents,
    exams,
    health,
    inside,
    journal,
    my_documents,
    plan,
    radar,
    students,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.journal.scheduler import is_enabled, watch_the_clock

    task = asyncio.create_task(watch_the_clock()) if is_enabled() else None
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(
    lifespan=lifespan,
    title="Sarathi",
    description="An agent that watches government exams for one student.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(radar.router)
app.include_router(exams.router)
app.include_router(documents.router)
app.include_router(my_documents.router)
app.include_router(journal.router)
app.include_router(plan.router)
app.include_router(changes.router)
app.include_router(inside.router)

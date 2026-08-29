from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, exams, health, radar, students

app = FastAPI(
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
app.include_router(students.router)
app.include_router(radar.router)
app.include_router(exams.router)
app.include_router(documents.router)

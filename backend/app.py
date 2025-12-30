from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.tf import router as tf_router
from backend.api.health import router as health_router
from backend.api.performance import router as performance_router
from backend.api.video import router as video_router
from backend.api.tf_video import router as tf_video_router
from backend.api.workout import router as workout_router
from backend.db.init_db import init_db
from backend.api.analytics import router as analytics_router
from backend.api.coach import router as coach_router

app = FastAPI(title="SmartFit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(coach_router)
app.include_router(tf_video_router)
app.include_router(tf_router)
app.include_router(health_router)
app.include_router(performance_router)
app.include_router(video_router)
app.include_router(workout_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"status": "SmartFit backend running"}

@app.on_event("startup")
def startup():
    init_db()

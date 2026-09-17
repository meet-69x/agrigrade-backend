import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.models import user, centre, batch, onion  # noqa: F401 - registers models
from app.routers import auth, batches, onions, centres
from seed import seed_initial_data

app = FastAPI(
    title="AgriGrade AI API",
    description="Backend for AI-powered onion quality grading at procurement centres.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.storage_dir, exist_ok=True)
app.mount("/storage/images", StaticFiles(directory=settings.storage_dir), name="images")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(centres.router)
app.include_router(batches.router)
app.include_router(onions.router)

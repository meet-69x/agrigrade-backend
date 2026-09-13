from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import user, centre, batch, onion  # noqa: F401 - registers models
from app.routers import auth, batches, onions, centres

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


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist. For production, switch to Alembic
    # migrations instead of create_all.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(centres.router)
app.include_router(batches.router)
app.include_router(onions.router)

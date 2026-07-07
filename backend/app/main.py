from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.ingestion.seed import seed
from app.routers import auth, company, insights, metrics
from app.security import ensure_demo_user

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(company.router)
app.include_router(metrics.router)
app.include_router(insights.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        # Called unconditionally (it's idempotent - checks for an existing
        # user by email first) rather than only inside seed()'s "already
        # seeded" branch. Without this, a run that seeds the financial data
        # successfully but then fails partway through creating the demo user
        # (e.g. the bcrypt/passlib version issue this project hit) would
        # commit the financial data and permanently skip ever creating the
        # login user on every subsequent restart, since seed() short-circuits
        # as soon as it sees the Company row already exists.
        ensure_demo_user(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

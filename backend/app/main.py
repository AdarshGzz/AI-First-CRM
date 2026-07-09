"""
FastAPI application entrypoint.
- CORS middleware for frontend access
- WebSocket router
- Startup: init DB tables, seed HCP profiles, connect Redis
- Shutdown: close connections
"""

from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.chat_ws import router as chat_router
from app.db.session import init_db, close_db
from app.db.seed import seed_hcp_profiles
from app.cache.redis_client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # ── Startup ──────────────────────────────────────────
    print("🚀 Starting AI-CRM Backend...")

    # Initialize database tables
    try:
        await init_db()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️  Database init failed: {e}")
        print("   Continuing without database — set NEON_DATABASE_URL in .env")

    # Seed HCP profiles
    try:
        await seed_hcp_profiles()
    except Exception as e:
        print(f"⚠️  HCP seed failed: {e}")

    print("✅ Backend ready!")

    yield

    # ── Shutdown ─────────────────────────────────────────
    print("🛑 Shutting down...")
    await close_db()
    close_redis()
    print("✅ Cleanup complete")


# ── App factory ──────────────────────────────────────────────

app = FastAPI(
    title="AI-CRM Interaction Logger",
    description="AI-driven CRM interaction logger for life science field reps",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────

app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "service": "AI-CRM Interaction Logger",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

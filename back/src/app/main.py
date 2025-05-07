from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlmodel import SQLModel

from app.api.v1 import asset_type
from app.auth import auth, security
from app.core.config import settings
from app.db.session import engine, get_session_raw
from app.utils.tracing import configure_tracer
from app.db.seed import seed_initial_data


from app.models.user import User
from app.models.asset_type import AssetType


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Seed initial data
    session = await get_session_raw()
    try:
        await seed_initial_data(session)
    finally:
        await session.close()
    
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"operationsSorter": "method", "defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

# configure metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, include_in_schema=False)

# configure tracing
configure_tracer(app)

origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers directly (not versioned APIRouter wrapper)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(asset_type.router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/me", tags=["Auth"])
async def read_current_user(user=Depends(security.get_current_user)):
    return {"id": str(user.id), "username": user.username, "email": user.email}

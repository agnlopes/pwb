from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlmodel import SQLModel

from app.api.v1 import asset_type
from app.auth import auth, security
from app.core.config import settings
from app.db.session import engine
from app.utils.tracing import configure_tracer


from app.models.user import User
from app.models.asset_type import AssetType

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "PWB - Portfolio Workbench: A multi-user portfolio management platform supporting a range of assets, "
        "ETFs, forecasting tools, macroeconomic indicators, and financial event awareness."
    ),
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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers directly (not versioned APIRouter wrapper)
app.include_router(auth.router, prefix="/api/v1")
# app.include_router(user.router, prefix="/api/v1")
# app.include_router(portfolio.router, prefix="/api/v1")
# app.include_router(holding.router, prefix="/api/v1", tags=["holding"])
# app.include_router(asset.router, prefix="/api/v1", tags=["asset"])
# app.include_router(etf.router, prefix="/api/v1", tags=["etf"])
# app.include_router(top_holding.router, prefix="/api/v1", tags=["top_holding"])
app.include_router(asset_type.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/me", tags=["Auth"])
async def read_current_user(user=Depends(security.get_current_user)):
    return {"id": str(user.id), "username": user.username, "email": user.email}

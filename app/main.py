from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import init_db
from app.routers.auth import router as auth_router
from app.routers.ingress import router as ingress_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Manara HA Addon", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(ingress_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

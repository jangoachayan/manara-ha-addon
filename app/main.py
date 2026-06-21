import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.ha_websocket import run_ha_websocket_listener
from app.core.mdns import register_mdns_service
from app.db.database import init_db
from app.routers.auth import router as auth_router
from app.routers.devices import router as devices_router
from app.routers.ingress import router as ingress_router
from app.routers.ws import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    asyncio.create_task(run_ha_websocket_listener())
    zeroconf_instance = register_mdns_service()
    yield
    zeroconf_instance.close()


app = FastAPI(title="Manara HA Addon", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(devices_router)
app.include_router(ingress_router)
app.include_router(ws_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from sqlmodel import Session
from starlette.background import BackgroundTask
from app.core.auth_dependency import get_current_device
from app.core.ha_client import get_states, get_state, call_service, stream_camera
from app.core.ha_registry import get_entity_area_map
from app.core.groups import get_groups_with_entities
from app.db.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/devices', tags=['devices'])

@router.get('/states')
async def get_device_states(device_id: str = Depends(get_current_device)) -> list[dict]:
    try:
        states = await get_states()
        return states
    except httpx.HTTPError as e:
        logger.error(f"HA API call failed: {e}")
        raise HTTPException(status_code=502, detail='Unable to reach Home Assistant') from e

@router.get('/areas')
async def get_device_areas(device_id: str = Depends(get_current_device)) -> dict[str, str]:
    try:
        area_map = await get_entity_area_map()
        return area_map
    except Exception as e:
        logger.error(f"HA registry call failed: {e}")
        raise HTTPException(status_code=502, detail='Unable to reach Home Assistant') from e

@router.post('/{entity_id}/toggle')
async def toggle_device(entity_id: str, device_id: str = Depends(get_current_device)) -> dict:
    try:
        current_state = await get_state(entity_id)
        domain = entity_id.split('.')[0]

        if current_state['state'] == 'on':
            await call_service(domain, 'turn_off', entity_id)
        else:
            await call_service(domain, 'turn_on', entity_id)

        new_state = await get_state(entity_id)
        return new_state
    except (httpx.HTTPError, Exception) as e:
        logger.error(f"HA toggle call failed: {e}")
        raise HTTPException(status_code=502, detail='Unable to reach Home Assistant') from e

@router.get('/groups')
async def get_groups(device_id: str = Depends(get_current_device), session: Session = Depends(get_session)) -> dict[str, list[str]]:
    try:
        return get_groups_with_entities(session)
    except Exception as e:
        logger.error(f"Failed to retrieve groups: {e}")
        raise HTTPException(status_code=500, detail='Unable to retrieve groups') from e

@router.get('/{entity_id}/stream')
async def stream_device(entity_id: str, device_id: str = Depends(get_current_device)) -> StreamingResponse:
    try:
        response = await stream_camera(entity_id)
    except httpx.HTTPError as e:
        logger.error(f"HA stream call failed: {e}")
        raise HTTPException(status_code=502, detail='Unable to reach Home Assistant') from e

    media_type = response.headers.get('content-type', 'multipart/x-mixed-replace')
    return StreamingResponse(
        content=response.aiter_bytes(),
        media_type=media_type,
        background=BackgroundTask(response.aclose),
    )

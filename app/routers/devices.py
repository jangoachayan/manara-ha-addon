import logging

from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.core.auth_dependency import get_current_device
from app.core.ha_client import get_states, get_state, call_service
from app.core.ha_registry import get_entity_area_map

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
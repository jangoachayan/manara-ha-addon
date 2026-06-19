import os
import httpx

HA_BASE_URL: str = 'http://supervisor/core/api'

def _get_headers() -> dict[str, str]:
    return {
        'Authorization': f'Bearer {os.environ["SUPERVISOR_TOKEN"]}',
        'Content-Type': 'application/json'
    }

async def get_states() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{HA_BASE_URL}/states', headers=_get_headers(), timeout=10.0)
        response.raise_for_status()
        return response.json()

async def get_state(entity_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{HA_BASE_URL}/states/{entity_id}', headers=_get_headers(), timeout=10.0)
        response.raise_for_status()
        return response.json()
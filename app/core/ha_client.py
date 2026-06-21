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

async def call_service(domain: str, service: str, entity_id: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{HA_BASE_URL}/services/{domain}/{service}',
            headers=_get_headers(),
            json={'entity_id': entity_id},
            timeout=10.0,
        )
        response.raise_for_status()

async def stream_camera(entity_id: str) -> httpx.Response:
    url = f'{HA_BASE_URL}/camera_proxy_stream/{entity_id}'
    client = httpx.AsyncClient(timeout=None)
    request = client.build_request('GET', url, headers=_get_headers())
    response = await client.send(request, stream=True)

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"stream_camera: status={response.status_code}, "
                f"content-type={response.headers.get('content-type')}, "
                f"url={url}")

    return response

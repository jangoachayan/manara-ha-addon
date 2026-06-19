import json
import os

import websockets

HA_WS_URL: str = 'ws://supervisor/core/websocket'

async def get_entity_area_map() -> dict[str, str]:
    websocket = await websockets.connect(HA_WS_URL)
    try:
        # Receive initial auth_required message
        response = await websocket.recv()
        if json.loads(response)['type'] != 'auth_required':
            raise RuntimeError('Unexpected initial message from HA WebSocket')

        # Send authentication request
        access_token = os.environ['SUPERVISOR_TOKEN']
        await websocket.send(json.dumps({'type': 'auth', 'access_token': access_token}))

        # Receive and confirm auth_ok response
        response = await websocket.recv()
        if json.loads(response)['type'] != 'auth_ok':
            raise RuntimeError('HA WebSocket authentication failed')

        msg_id = 1

        # Query area registry
        await websocket.send(json.dumps({'id': msg_id, 'type': 'config/area_registry/list'}))
        response = await websocket.recv()
        areas = json.loads(response).get('result', [])
        area_map: dict[str, str] = {area['area_id']: area['name'] for area in areas}
        msg_id += 1

        # Query device registry
        await websocket.send(json.dumps({'id': msg_id, 'type': 'config/device_registry/list'}))
        response = await websocket.recv()
        devices = json.loads(response).get('result', [])
        device_map: dict[str, str | None] = {device['id']: device.get('area_id') for device in devices}
        msg_id += 1

        # Query entity registry
        await websocket.send(json.dumps({'id': msg_id, 'type': 'config/entity_registry/list'}))
        response = await websocket.recv()
        entities = json.loads(response).get('result', [])

        entity_area_map: dict[str, str] = {}
        for entity in entities:
            entity_id = entity['entity_id']
            area_id = entity.get('area_id')
            if not area_id and entity.get('device_id'):
                area_id = device_map.get(entity['device_id'])
            area_name = area_map.get(area_id, 'Unassigned')
            entity_area_map[entity_id] = area_name

        return entity_area_map
    finally:
        await websocket.close()

import asyncio
import json
import logging
import os
import websockets
import websockets.exceptions
from app.core.event_bus import event_bus

logger = logging.getLogger(__name__)

HA_WS_URL: str = 'ws://supervisor/core/websocket'
SENSOR_THRESHOLDS: dict[str, float] = {'temperature': 0.5, 'humidity': 2.0}
_last_published_values: dict[str, float] = {}

async def run_ha_websocket_listener() -> None:
    while True:
        try:
            async with websockets.connect(HA_WS_URL) as websocket:
                # Receive the auth_required handshake message before authenticating
                await websocket.recv()

                # Authenticate
                auth_message = {'type': 'auth', 'access_token': os.environ['SUPERVISOR_TOKEN']}
                await websocket.send(json.dumps(auth_message))
                auth_response = json.loads(await websocket.recv())
                if auth_response.get('type') != 'auth_ok':
                    logger.error("Authentication failed: %s", auth_response)
                    continue

                # Subscribe to state_changed events
                subscribe_message = {'id': 1, 'type': 'subscribe_events', 'event_type': 'state_changed'}
                await websocket.send(json.dumps(subscribe_message))
                subscription_confirmation = json.loads(await websocket.recv())
                if not subscription_confirmation.get('success'):
                    logger.error("Subscription failed: %s", subscription_confirmation)
                    continue

                # Process incoming messages
                async for message in websocket:
                    try:
                        message_data = json.loads(message)
                        if message_data.get('type') == 'event' and 'event' in message_data:
                            new_state = message_data['event']['data']['new_state']
                            entity_id = new_state['entity_id']
                            state = new_state['state']
                            attributes = new_state.get('attributes', {})

                            # Apply threshold filtering
                            for key, threshold in SENSOR_THRESHOLDS.items():
                                if key in entity_id:
                                    try:
                                        float_state = float(state)
                                        last_value = _last_published_values.get(entity_id, float('-inf'))
                                        if abs(float_state - last_value) >= threshold:
                                            await event_bus.publish({'entity_id': entity_id, 'state': state, 'attributes': attributes})
                                            _last_published_values[entity_id] = float_state
                                    except ValueError:
                                        # Non-numeric state, publish unconditionally
                                        await event_bus.publish({'entity_id': entity_id, 'state': state, 'attributes': attributes})
                                    break
                            else:
                                # No matching threshold key, publish unconditionally
                                await event_bus.publish({'entity_id': entity_id, 'state': state, 'attributes': attributes})

                    except Exception as e:
                        logger.error("Error processing message: %s", e)

        except (websockets.exceptions.ConnectionClosed, Exception) as e:
            logger.warning("Connection closed or error occurred: %s", e)
            await asyncio.sleep(5)
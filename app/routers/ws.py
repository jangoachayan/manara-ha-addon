from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError
from app.core.security import decode_token
from app.core.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)

MAX_CONNECTIONS: int = 10
active_connections: int = 0

router = APIRouter()

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    global active_connections
    
    try:
        decode_token(token)
    except JWTError:
        await websocket.close(code=1008, reason='Invalid token')
        return
    
    if active_connections >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason='Too many connections')
        return
    
    await websocket.accept()
    active_connections += 1
    queue = event_bus.subscribe()
    
    try:
        while True:
            message = await queue.get()
            await websocket.send_json(message)
    except WebSocketDisconnect as e:
        logger.info(f"Client disconnected with code {e.code}")
    finally:
        event_bus.unsubscribe(queue)
        active_connections -= 1
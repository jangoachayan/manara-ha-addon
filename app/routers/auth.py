import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session
from app.models.auth import PairRequest, TokenResponse
from app.db.database import get_session
from app.db.models import Device
from app.core.pairing import (
    get_valid_pairing_code,
    consume_pairing_code,
    create_pairing_code,
    generate_qr_code_image,
)
from app.core.security import create_access_token, create_refresh_token
from app.core.config import MANARA_TUNNEL_URL

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/pair')
async def pair(pair_request: PairRequest, session: Session = Depends(get_session)) -> TokenResponse:
    pairing_code = get_valid_pairing_code(session, pair_request.pairing_code)
    if pairing_code is None:
        raise HTTPException(status_code=400, detail='Invalid or expired pairing code')

    consume_pairing_code(session, pairing_code)

    device = Device(device_id=pair_request.device_id, device_name=pair_request.device_name)
    session.add(device)
    session.commit()

    access_token = create_access_token(data={'sub': pair_request.device_id})
    refresh_token = create_refresh_token(data={'sub': pair_request.device_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer',
        expires_in=900,
    )


@router.get('/qr')
async def qr(session: Session = Depends(get_session)) -> Response:
    pairing_code = create_pairing_code(session)

    qr_payload = {
        'mdns': '_manara._tcp.local',
        'remote': MANARA_TUNNEL_URL,
        'code': pairing_code.code,
    }

    png_bytes = generate_qr_code_image(json.dumps(qr_payload))

    return Response(content=png_bytes, media_type='image/png')

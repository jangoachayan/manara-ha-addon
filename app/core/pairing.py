from datetime import datetime, timedelta
from typing import Optional
import secrets
import io
import qrcode
from sqlmodel import Session, select
from app.db.models import PairingCode

PAIRING_CODE_LENGTH: int = 8
PAIRING_CODE_ALPHABET: str = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
PAIRING_CODE_EXPIRY_MINUTES: int = 10

def generate_pairing_code() -> str:
    return ''.join(secrets.choice(PAIRING_CODE_ALPHABET) for _ in range(PAIRING_CODE_LENGTH))

def create_pairing_code(session: Session) -> PairingCode:
    code = generate_pairing_code()
    pairing_code = PairingCode(
        code=code,
        used=False,
        expires_at=datetime.utcnow() + timedelta(minutes=PAIRING_CODE_EXPIRY_MINUTES)
    )
    session.add(pairing_code)
    session.commit()
    session.refresh(pairing_code)
    return pairing_code

def get_valid_pairing_code(session: Session, code: str) -> Optional[PairingCode]:
    statement = select(PairingCode).where(
        PairingCode.code == code,
        PairingCode.used == False,
        PairingCode.expires_at > datetime.utcnow()
    )
    result = session.execute(statement)
    return result.scalar_one_or_none()

def consume_pairing_code(session: Session, pairing_code: PairingCode) -> None:
    pairing_code.used = True
    session.add(pairing_code)
    session.commit()

def generate_qr_code_image(data: str) -> bytes:
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')  # type: ignore[call-arg]  # types-qrcode types make() as PyPNGImage, but Pillow is installed so this is actually a PilImage, whose save() accepts format=
    return buffer.getvalue()
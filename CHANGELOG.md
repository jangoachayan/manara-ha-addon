# Changelog

## [0.3.1] - 2026-06-18

### Added
- Ingress web UI at / showing QR code for device pairing
- Health and API docs links on the ingress page

## [0.3.0] - 2026-06-18

### Added
- POST /auth/pair endpoint: validates QR pairing code, registers device, issues JWT
  access and refresh tokens
- GET /auth/qr endpoint: generates a new pairing code and returns it as a PNG QR
  image encoding {mdns, remote, code} payload
- app/main.py: FastAPI lifespan wiring init_db() on startup, auth router included

## [0.2.0] - 2026-06-16

### Added
- Cloudflare Tunnel integration: cloudflared now runs inside the addon container,
  establishing an outbound quick tunnel on startup and logging the assigned
  trycloudflare.com URL for remote mobile app access
- app/core/config.py: MANARA_TUNNEL_URL environment variable for QR pairing payload

### Changed
- run.sh: cloudflared starts before uvicorn, tunnel URL extracted and exported before
  FastAPI app starts

## [0.1.0] - 2026-06-15

### Added
- Initial release: FastAPI backend packaged as a Home Assistant add-on
- JWT-based authentication helpers (app/core/security.py)
- QR-based device pairing data models (app/models/auth.py)
- SQLModel database setup with PairingCode and Device tables
- Pairing code generation, validation, and QR image rendering (app/core/pairing.py)
- Home Assistant add-on packaging (config.yaml, Dockerfile, run.sh, repository.yaml)
- Manara MA monogram icon and logo

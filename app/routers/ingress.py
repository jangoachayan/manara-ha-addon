from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manara Backend</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 480px;
            box-sizing: border-box;
        }
        header {
            background-color: #5a2f82;
            color: white;
            text-align: center;
            padding: 16px 0;
        }
        section {
            padding: 0 20px 20px;
        }
        .status a {
            display: block;
            margin-bottom: 5px;
            color: #5a2f82;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>Manara Backend</header>
        <section class="pair-device">
            <h2>Pair a Device</h2>
            <p>Scan this QR code with the Manara app to pair your device. The code expires in 10 minutes.</p>
            <img src="/auth/qr" width="256" height="256" alt="Pairing QR code">
            <button onclick="window.location.reload()">Refresh</button>
        </section>
        <section class="status">
            <h2>Status</h2>
            <a href="/health" target="_blank">Health</a>
            <a href="/docs" target="_blank">API Docs</a>
        </section>
    </div>
</body>
</html>
"""


@router.get("/")
async def ingress_ui() -> HTMLResponse:
    return HTMLResponse(content=HTML_CONTENT, status_code=200)

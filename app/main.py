from fastapi import FastAPI

app = FastAPI(title="Manara HA Addon")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

"""Punto de entrada HTTP (cliente-servidor) para AnaDec."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import router

app = FastAPI(title="AnaDec API")

# CORS es necesario en desarrollo porque el navegador bloquea por defecto
# peticiones cross-origin entre frontend (puertos 5173/3000) y backend (otro puerto).
# Esta configuracion permite solo esos origins locales para DEV.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Ejecutar local:
# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

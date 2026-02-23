from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import router

app = FastAPI(title="AnaDec API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Ejecutar local:
# uvicorn src.main:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, entries

app = FastAPI(
    title="Pulsr API",
    description="Daily timeline tracker backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to specific frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}

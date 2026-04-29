from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import activities, auth, categories, entries, insights, projects

app = FastAPI(
    title="Pulsr API",
    description="Daily timeline tracker backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tracker.pulsr.in",
        "https://www.tracker.pulsr.in",
        "http://localhost:3000",
        "http://192.168.29.177:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(projects.router)
app.include_router(categories.router)
app.include_router(activities.router)
app.include_router(insights.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}

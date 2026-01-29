from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.clock import router as clock_router
from app.api.replay import router as replay_router


app = FastAPI(title="F1 Replay API")

app.include_router(health_router)
app.include_router(clock_router)
app.include_router(replay_router)

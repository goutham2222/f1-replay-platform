# app/api/clock.py

from fastapi import APIRouter, Query
from app.services.clock_registry import clock

router = APIRouter(prefix="/clock")


@router.get("/state")
def get_state():
    return clock.snapshot()


@router.post("/play")
def play():
    clock.play()
    return clock.snapshot()


@router.post("/pause")
def pause():
    clock.pause()
    return clock.snapshot()


@router.post("/reset")
def reset():
    clock.reset()
    return clock.snapshot()


@router.post("/tick")
def tick(base_ms: int = Query(1000, ge=1)):
    clock.tick(base_ms)
    return clock.snapshot()


@router.post("/seek")
def seek(target_time_ms: int = Query(..., ge=0)):
    clock.seek(target_time_ms)
    return clock.snapshot()


@router.post("/seek/next-lap")
def next_lap():
    clock.seek_next_lap()
    return clock.snapshot()


@router.post("/seek/previous-lap")
def previous_lap():
    clock.seek_previous_lap()
    return clock.snapshot()

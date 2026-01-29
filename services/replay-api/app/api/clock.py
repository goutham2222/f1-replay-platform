from fastapi import APIRouter, HTTPException
from app.services.clock_registry import clock

router = APIRouter(prefix="/clock")


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


@router.post("/seek")
def seek(time_ms: int):
    try:
        clock.seek(time_ms)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return clock.snapshot()


@router.post("/advance")
def advance(ms: int):
    try:
        clock.advance(ms)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return clock.snapshot()


@router.post("/speed")
def set_speed(speed: float):
    try:
        clock.set_speed(speed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return clock.snapshot()


@router.post("/tick")
def tick(base_ms: int = 1000):
    """
    Deterministic auto-advance step.
    UI or tests call this repeatedly.
    """
    clock.tick(base_ms)
    return clock.snapshot()


@router.get("/state")
def state():
    return clock.snapshot()

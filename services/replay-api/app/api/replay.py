# app/api/replay.py

from fastapi import APIRouter
from app.services.frame_builder import FrameBuilder
from app.services.clock_registry import clock
from app.core.config import settings

router = APIRouter(prefix="/replay")

# FrameBuilder is initialized once (startup-safe)
frame_builder = FrameBuilder(
    curated_bucket=settings.curated_bucket,
    season=settings.default_season,
    round=settings.default_round,
)


@router.get("/frame")
def get_frame():
    """
    Return a deterministic replay frame for the current simulation time.
    """

    return frame_builder.build_frame()

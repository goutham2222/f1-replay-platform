from fastapi import APIRouter
from app.services.clock_registry import clock
from app.services.frame_builder import FrameBuilder
from app.core.config import settings

router = APIRouter(prefix="/replay")

frame_builder = FrameBuilder(
    curated_bucket=settings.curated_bucket,
    season=settings.default_season,
    round=settings.default_round,
)


@router.get("/frame")
def get_frame():
    """
    Returns replay frame at current simulation time.
    """
    return frame_builder.build_frame(clock.current_time_ms)


@router.get("/metadata")
def get_metadata():
    """
    Returns static replay metadata for UI bootstrap.
    """
    return {
        "race": frame_builder.race,
        "drivers": frame_builder.drivers.to_dict(orient="records"),
        "season": frame_builder.season,
        "round": frame_builder.round,
    }
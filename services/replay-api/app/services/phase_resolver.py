from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LapWindow:
    lap_number: int
    start_ms: int
    finish_ms: int


class PhaseResolver:
    def __init__(self, lap_windows: List[LapWindow]):
        if not lap_windows:
            raise ValueError("lap_windows cannot be empty")

        self.lap_windows = sorted(lap_windows, key=lambda x: x.lap_number)
        self.race_start_ms = self.lap_windows[0].start_ms
        self.race_finish_ms = self.lap_windows[-1].finish_ms

    def resolve_phase(self, current_time_ms: int) -> str:
        if current_time_ms < self.race_start_ms:
            return "PRE_RACE"
        if current_time_ms >= self.race_finish_ms:
            return "FINISHED"
        return "GREEN"

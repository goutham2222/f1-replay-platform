from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

import arcade

from clients.arcade.s3_track_loader import load_track_from_s3


@dataclass
class _Transform:
    scale: float
    offset_x: float
    offset_y: float


class TrackRenderer:
    def __init__(self):
        self.points: List[Tuple[float, float]] = []
        self._transform: Optional[_Transform] = None

    def load_from_s3(self, bucket: str, season: int, round_: int):
        self.points = load_track_from_s3(
            bucket=bucket,
            season=season,
            round_=round_,
            dataset="track_geometry",
        )
        self._transform = None  # recompute when we know window size

    def fit_to_view(self, width: int, height: int, padding: int = 60):
        if not self.points:
            self._transform = _Transform(1.0, 0.0, 0.0)
            return

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)

        usable_w = max(width - 2 * padding, 10)
        usable_h = max(height - 2 * padding, 10)

        # Preserve aspect ratio: uniform scale
        scale = min(usable_w / span_x, usable_h / span_y)

        # Center in view
        track_cx = (min_x + max_x) / 2.0
        track_cy = (min_y + max_y) / 2.0
        screen_cx = width / 2.0
        screen_cy = height / 2.0

        offset_x = screen_cx - track_cx * scale
        offset_y = screen_cy - track_cy * scale

        self._transform = _Transform(scale=scale, offset_x=offset_x, offset_y=offset_y)

    def to_screen(self, x: float, y: float) -> Tuple[float, float]:
        if self._transform is None:
            # Safe default (won't freeze). Main window will call fit_to_view() early.
            return x, y
        t = self._transform
        return (x * t.scale + t.offset_x, y * t.scale + t.offset_y)

    def draw(self):
        if not self.points:
            return
        if self._transform is None:
            # If fit_to_view() wasn’t called yet, we still draw raw (debug)
            pts = self.points
        else:
            pts = [self.to_screen(x, y) for (x, y) in self.points]

        arcade.draw_line_strip(pts, arcade.color.WHITE, 2)

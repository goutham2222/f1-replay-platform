import arcade
from typing import List, Tuple
import math

from clients.arcade.s3_track_loader import load_track_from_s3


class TrackRenderer:
    TRACK_HALF_WIDTH = 6
    UI_TOP_MARGIN = 120
    SIDE_PADDING = 60
    BOTTOM_PADDING = 60

    def __init__(self):
        self.points: List[Tuple[float, float]] = []
        self._transform = None
        self.inner: List[Tuple[float, float]] = []
        self.outer: List[Tuple[float, float]] = []

    # -------------------------
    # Data loading
    # -------------------------
    def load_from_s3(self, bucket: str, season: int, round_: int):
        self.points = load_track_from_s3(bucket, season, round_)
        if not self.points:
            raise ValueError("Empty track geometry")

    # -------------------------
    # Layout / transform
    # -------------------------
    def fit_to_view(self, window_width: float, window_height: float):
        drawable_width = window_width - self.SIDE_PADDING * 2
        drawable_height = (
            window_height
            - self.UI_TOP_MARGIN
            - self.BOTTOM_PADDING
        )

        self._compute_transform(drawable_width, drawable_height)
        self._build_boundaries()

    def _compute_transform(self, drawable_w: float, drawable_h: float):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        scale = min(
            drawable_w / (max_x - min_x),
            drawable_h / (max_y - min_y),
        )

        track_w = (max_x - min_x) * scale
        track_h = (max_y - min_y) * scale

        offset_x = (drawable_w - track_w) / 2 - min_x * scale + self.SIDE_PADDING
        offset_y = (
            self.BOTTOM_PADDING
            + (drawable_h - track_h) / 2
            - min_y * scale
        )

        self._transform = (scale, offset_x, offset_y)

    def to_screen(self, x: float, y: float):
        scale, ox, oy = self._transform
        return x * scale + ox, y * scale + oy

    # -------------------------
    # Geometry
    # -------------------------
    def _build_boundaries(self):
        n = len(self.points)
        inner = []
        outer = []

        for i in range(n):
            p_prev = self.points[i - 1]
            p_curr = self.points[i]
            p_next = self.points[(i + 1) % n]

            dx = p_next[0] - p_prev[0]
            dy = p_next[1] - p_prev[1]
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            nx = -dy / length
            ny = dx / length

            ix = p_curr[0] - nx * self.TRACK_HALF_WIDTH
            iy = p_curr[1] - ny * self.TRACK_HALF_WIDTH
            ox = p_curr[0] + nx * self.TRACK_HALF_WIDTH
            oy = p_curr[1] + ny * self.TRACK_HALF_WIDTH

            inner.append(self.to_screen(ix, iy))
            outer.append(self.to_screen(ox, oy))

        self.inner = inner
        self.outer = outer

    # -------------------------
    # Rendering
    # -------------------------
    def draw(self):
        if not self.inner:
            return

        arcade.draw_line_strip(
            self.outer + [self.outer[0]],
            arcade.color.LIGHT_GRAY,
            3,
        )
        arcade.draw_line_strip(
            self.inner + [self.inner[0]],
            arcade.color.GRAY,
            3,
        )

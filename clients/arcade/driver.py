import arcade


class DriverDot:
    def __init__(self, color, radius: int = 6):
        self.color = color
        self.radius = radius

        # Previous + target positions
        self.prev_x = None
        self.prev_y = None
        self.target_x = None
        self.target_y = None

        # Timing
        self.prev_time_ms = None
        self.target_time_ms = None

    def update(self, x: float, y: float, time_ms: int):
        """
        Called ONLY when a new replay frame arrives.
        """
        if self.target_x is None:
            # First-ever position
            self.prev_x = x
            self.prev_y = y
            self.target_x = x
            self.target_y = y
            self.prev_time_ms = time_ms
            self.target_time_ms = time_ms
            return

        # Shift target → previous
        self.prev_x = self.target_x
        self.prev_y = self.target_y
        self.prev_time_ms = self.target_time_ms

        self.target_x = x
        self.target_y = y
        self.target_time_ms = time_ms

    def draw(self, render_time_ms: int):
        if self.prev_x is None or self.target_x is None:
            return

        if self.target_time_ms == self.prev_time_ms:
            t = 1.0
        else:
            t = (
                (render_time_ms - self.prev_time_ms)
                / (self.target_time_ms - self.prev_time_ms)
            )
            t = max(0.0, min(1.0, t))

        x = self.prev_x + (self.target_x - self.prev_x) * t
        y = self.prev_y + (self.target_y - self.prev_y) * t

        arcade.draw_circle_filled(x, y, self.radius, self.color)

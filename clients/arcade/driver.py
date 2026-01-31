import arcade


class DriverDot:
    def __init__(self, color, radius: float = 6.0):
        self.color = color
        self.radius = radius

        self.prev = None
        self.curr = None

    def update(self, x: float, y: float):
        self.prev = self.curr
        self.curr = (x, y)

    def draw(self, alpha: float):
        if self.curr is None:
            return

        if self.prev is None:
            x, y = self.curr
        else:
            x = self.prev[0] + (self.curr[0] - self.prev[0]) * alpha
            y = self.prev[1] + (self.curr[1] - self.prev[1]) * alpha

        arcade.draw_circle_filled(x, y, self.radius, self.color)

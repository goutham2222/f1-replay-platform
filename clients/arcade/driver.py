import arcade


class DriverDot:
    def __init__(self, color=arcade.color.YELLOW, radius: float = 6.0):
        self.color = color
        self.radius = radius

    def draw(self, x: float, y: float):
        arcade.draw_circle_filled(x, y, self.radius, self.color)

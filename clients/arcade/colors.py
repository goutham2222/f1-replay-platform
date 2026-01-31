import arcade

_DRIVER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.GREEN,
    arcade.color.YELLOW,
    arcade.color.ORANGE,
    arcade.color.PURPLE,
    arcade.color.CYAN,
    arcade.color.MAGENTA,
    arcade.color.WHITE,
]


def get_driver_color(index: int):
    return _DRIVER_COLORS[index % len(_DRIVER_COLORS)]

import arcade

TEAM_COLORS = {
    "Red Bull": arcade.color.DARK_BLUE,
    "Ferrari": arcade.color.RED,
    "Mercedes": arcade.color.SILVER,
    "McLaren": arcade.color.ORANGE,
    "Aston Martin": arcade.color.DARK_GREEN,
    "Alpine": arcade.color.BLUE,
    "Williams": arcade.color.LIGHT_BLUE,
    "AlphaTauri": arcade.color.WHITE,
    "Alfa Romeo": arcade.color.MAROON,
    "Haas": arcade.color.GRAY,
}


def get_team_color(team_name: str):
    return TEAM_COLORS.get(team_name, arcade.color.YELLOW)

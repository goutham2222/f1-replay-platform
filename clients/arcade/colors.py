import arcade

TEAM_COLORS = {
    "Red Bull Racing": arcade.color.DARK_BLUE,
    "Ferrari": arcade.color.RED,
    "Mercedes": arcade.color.SILVER,
    "McLaren": arcade.color.ORANGE,
    "Aston Martin": arcade.color.DARK_GREEN,
    "Alpine": arcade.color.BLUE,
    "Williams": arcade.color.LIGHT_BLUE,
    "AlphaTauri": arcade.color.WHITE,
    "Alfa Romeo": arcade.color.MAROON,
    "Haas F1 Team": arcade.color.GRAY,
}


def get_team_color(team: str):
    """Get the color for a team, defaulting to white if not found."""
    return TEAM_COLORS.get(team, arcade.color.WHITE)


def format_race_time(ms: int) -> str:
    """
    Format milliseconds into HH:MM:SS.
    Example: 01:12:34
    """
    total_seconds = ms // 1000

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

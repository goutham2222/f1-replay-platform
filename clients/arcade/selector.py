import arcade


class ReplaySelector:
    def __init__(self):
        self.active = True

        self.seasons = [2023]
        self.rounds = list(range(1, 23))
        self.sessions = ["RACE"]

        self.season_idx = 0
        self.round_idx = 0
        self.session_idx = 0

        self.cursor = 0  # 0=season, 1=round, 2=session

    @property
    def season(self):
        return self.seasons[self.season_idx]

    @property
    def round(self):
        return self.rounds[self.round_idx]

    @property
    def session(self):
        return self.sessions[self.session_idx]

    def on_key(self, symbol):
        if symbol == arcade.key.UP:
            self.cursor = (self.cursor - 1) % 3

        elif symbol == arcade.key.DOWN:
            self.cursor = (self.cursor + 1) % 3

        elif symbol == arcade.key.LEFT:
            self._change(-1)

        elif symbol == arcade.key.RIGHT:
            self._change(1)

        elif symbol == arcade.key.ENTER:
            self.active = False

    def _change(self, delta):
        if self.cursor == 0:
            self.season_idx = (self.season_idx + delta) % len(self.seasons)
        elif self.cursor == 1:
            self.round_idx = (self.round_idx + delta) % len(self.rounds)
        elif self.cursor == 2:
            self.session_idx = (self.session_idx + delta) % len(self.sessions)

    def draw(self, width, height):
        arcade.draw_text(
            "F1 REPLAY SELECTOR",
            width / 2,
            height - 120,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )

        lines = [
            f"Season: {self.season}",
            f"Round: {self.round}",
            f"Session: {self.session}",
        ]

        for i, text in enumerate(lines):
            color = arcade.color.YELLOW if i == self.cursor else arcade.color.GRAY
            arcade.draw_text(
                text,
                width / 2,
                height - 200 - i * 40,
                color,
                18,
                anchor_x="center",
            )

        arcade.draw_text(
            "↑↓ Select   ←→ Change   ENTER Start",
            width / 2,
            60,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

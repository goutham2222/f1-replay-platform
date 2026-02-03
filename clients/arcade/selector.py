import arcade


class Dropdown:
    def __init__(self, label: str, options: list, selected_idx: int = 0):
        self.label = label
        self.options = options
        self.selected_idx = selected_idx
        self.open = False

    @property
    def value(self):
        return self.options[self.selected_idx]

    def move(self, delta: int):
        self.selected_idx = (self.selected_idx + delta) % len(self.options)


class ReplaySelector:
    def __init__(self):
        self.active = True

        self.dropdowns = [
            Dropdown("Season", [2023]),
            Dropdown("Round", list(range(1, 23))),
            Dropdown("Session", ["RACE"]),
        ]

        self.cursor = 0  # which dropdown / button is focused
        self.start_idx = len(self.dropdowns)  # START button index

    # --------------------------------------------------
    # Selected values
    # --------------------------------------------------
    @property
    def season(self):
        return self.dropdowns[0].value

    @property
    def round(self):
        return self.dropdowns[1].value

    @property
    def session(self):
        return self.dropdowns[2].value

    # --------------------------------------------------
    # Input
    # --------------------------------------------------
    def on_key(self, symbol):
        current = (
            self.dropdowns[self.cursor]
            if self.cursor < self.start_idx
            else None
        )

        # -------------------------------
        # Dropdown open
        # -------------------------------
        if current and current.open:
            if symbol == arcade.key.UP:
                current.move(-1)
            elif symbol == arcade.key.DOWN:
                current.move(1)
            elif symbol in (arcade.key.ENTER, arcade.key.ESCAPE):
                current.open = False
            return

        # -------------------------------
        # Navigation
        # -------------------------------
        if symbol == arcade.key.UP:
            self.cursor = (self.cursor - 1) % (self.start_idx + 1)

        elif symbol == arcade.key.DOWN:
            self.cursor = (self.cursor + 1) % (self.start_idx + 1)

        elif symbol == arcade.key.ENTER:
            if self.cursor == self.start_idx:
                self.active = False  # START
            else:
                current.open = True

    # --------------------------------------------------
    # Draw
    # --------------------------------------------------
    def draw(self, width, height):
        center_x = width / 2
        start_y = height - 140

        arcade.draw_text(
            "F1 REPLAY SELECTOR",
            center_x,
            start_y + 60,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )

        for idx, dropdown in enumerate(self.dropdowns):
            y = start_y - idx * 50
            focused = idx == self.cursor

            label_color = (
                arcade.color.YELLOW if focused else arcade.color.GRAY
            )

            arcade.draw_text(
                f"{dropdown.label}: {dropdown.value}",
                center_x,
                y,
                label_color,
                18,
                anchor_x="center",
            )

            if dropdown.open:
                for i, opt in enumerate(dropdown.options):
                    oy = y - 30 - i * 22
                    color = (
                        arcade.color.WHITE
                        if i == dropdown.selected_idx
                        else arcade.color.LIGHT_GRAY
                    )
                    arcade.draw_text(
                        f"- {opt}",
                        center_x,
                        oy,
                        color,
                        14,
                        anchor_x="center",
                    )

        # START button
        start_y_btn = start_y - self.start_idx * 50
        start_color = (
            arcade.color.GREEN
            if self.cursor == self.start_idx
            else arcade.color.GRAY
        )

        arcade.draw_text(
            "START",
            center_x,
            start_y_btn,
            start_color,
            20,
            anchor_x="center",
        )

        arcade.draw_text(
            "↑↓ Navigate   ENTER Select   ESC Close",
            center_x,
            50,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

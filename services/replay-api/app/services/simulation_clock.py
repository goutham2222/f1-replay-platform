class SimulationClock:
    def __init__(self, phase_resolver=None):
        self.phase_resolver = phase_resolver
        self.current_time_ms = 0
        self.playing = False
        self.phase = "PRE_RACE"

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def reset(self):
        self.current_time_ms = 0
        self.phase = "PRE_RACE"
        self.playing = False

    def seek(self, target_time_ms: int):
        self.current_time_ms = max(0, target_time_ms)

        if self.phase_resolver:
            self.phase = self.phase_resolver.resolve_phase(
                self.current_time_ms
            )

        self.playing = True

    def tick(self, delta_ms: int):
        if not self.playing:
            return

        self.current_time_ms += delta_ms

        if self.phase_resolver:
            self.phase = self.phase_resolver.resolve_phase(
                self.current_time_ms
            )

    def snapshot(self):
        total_seconds = self.current_time_ms // 1000
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        return {
            "current_time_ms": self.current_time_ms,
            "current_time_hms": f"{h:02d}:{m:02d}:{s:02d}",
            "playing": self.playing,
            "phase": self.phase,
        }

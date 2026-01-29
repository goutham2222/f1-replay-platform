from enum import Enum


class ClockState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"


class SimulationClock:
    """
    Deterministic simulation clock.
    Time advances only via controlled ticks or explicit calls.
    """

    def __init__(self):
        self.current_time_ms: int = 0
        self.state: ClockState = ClockState.PAUSED
        self.speed: float = 1.0  # playback multiplier

    # ----------------------------
    # State controls
    # ----------------------------
    def play(self):
        self.state = ClockState.PLAYING

    def pause(self):
        self.state = ClockState.PAUSED

    def reset(self):
        self.current_time_ms = 0
        self.state = ClockState.PAUSED
        self.speed = 1.0
        return self.current_time_ms

    # ----------------------------
    # Time controls
    # ----------------------------
    def seek(self, ms: int):
        if ms < 0:
            raise ValueError("Simulation time cannot be negative")
        self.current_time_ms = ms
        return self.current_time_ms

    def advance(self, ms: int):
        if ms < 0:
            raise ValueError("Cannot advance by negative milliseconds")
        self.current_time_ms += ms
        return self.current_time_ms

    def set_speed(self, speed: float):
        if speed <= 0:
            raise ValueError("Speed must be > 0")
        self.speed = speed

    # ----------------------------
    # Auto-advance tick
    # ----------------------------
    def tick(self, base_ms: int = 1000):
        """
        Advance time if clock is playing.
        Deterministic: no wall clock usage.
        """
        if self.state == ClockState.PLAYING:
            self.current_time_ms += int(base_ms * self.speed)

        return self.current_time_ms

    # ----------------------------
    # Snapshot
    # ----------------------------
    def snapshot(self) -> dict:
        return {
            "current_time_ms": self.current_time_ms,
            "state": self.state,
            "speed": self.speed,
        }

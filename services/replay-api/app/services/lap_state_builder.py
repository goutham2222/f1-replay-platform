class LapStateBuilder:
    def __init__(self, lap_times_df):
        self.df = lap_times_df

    def build(self, replay_time_ms: int):
        driver_states = []

        for driver_id, group in self.df.groupby("driver_id"):
            group = group.sort_values("lap_number")

            cumulative = group["lap_time_ms"].cumsum()
            completed = cumulative[cumulative <= replay_time_ms]

            if completed.empty:
                current_lap = 0
                last_lap_time = None
            else:
                idx = completed.index[-1]
                current_lap = group.loc[idx, "lap_number"]
                last_lap_time = group.loc[idx, "lap_time_ms"]

            driver_states.append({
                "driver_id": driver_id,
                "current_lap": int(current_lap),
                "last_completed_lap_time_ms": (
                    int(last_lap_time) if last_lap_time is not None else None
                )
            })

        return driver_states

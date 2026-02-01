def resolve_driver_status(driver_id: str, time_ms: int) -> str:
    """
    Deterministic placeholder driver status resolver.

    Rules:
    - Default: Racing
    - Pit window for selected drivers
    - Out after a fixed time for one driver
    """

    # --- Pit stop window (placeholder) ---
    if 120_000 <= time_ms < 150_000:
        if driver_id in {"16", "44"}:
            return "Pit"

    # --- Retirement placeholder ---
    if time_ms >= 240_000:
        if driver_id in {"11"}:
            return "Out"

    return "Racing"

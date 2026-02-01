# app/services/time_utils.py

def ms_to_hms(ms: int) -> str:
    """
    Convert milliseconds to HH:MM:SS
    """
    seconds = ms // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

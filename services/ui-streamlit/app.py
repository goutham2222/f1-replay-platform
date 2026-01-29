import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env (local dev)
load_dotenv()

REPLAY_API_BASE_URL = os.getenv("REPLAY_API_BASE_URL", "http://localhost:8000").rstrip("/")
DEFAULT_SEASON = int(os.getenv("DEFAULT_SEASON", "2023"))
DEFAULT_ROUND = int(os.getenv("DEFAULT_ROUND", "1"))

st.set_page_config(page_title="F1 Replay Platform", layout="wide")

st.title("F1 Replay Platform — Replay UI (Sprint 4)")

with st.sidebar:
    st.header("Configuration")
    st.caption("Local dev config is loaded from .env")

    api_base = st.text_input("Replay API Base URL", REPLAY_API_BASE_URL)
    season = st.number_input("Season", min_value=1950, max_value=2100, value=DEFAULT_SEASON, step=1)
    rnd = st.number_input("Round", min_value=1, max_value=30, value=DEFAULT_ROUND, step=1)

    st.divider()
    st.header("Clock Controls")
    tick_seconds = st.number_input("Tick seconds", min_value=0.0, value=1.0, step=0.5)

def _get(url: str, timeout: float = 10.0):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

def _post(url: str, json_body=None, timeout: float = 10.0):
    r = requests.post(url, json=json_body, timeout=timeout)
    r.raise_for_status()
    return r.json()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Clock State")
    if st.button("Refresh /clock/state"):
        try:
            data = _get(f"{api_base.rstrip('/')}/clock/state")
            st.json(data)
        except Exception as e:
            st.error(f"Failed to fetch clock state: {e}")

with col2:
    st.subheader("Actions")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Tick /clock/tick"):
            try:
                data = _post(f"{api_base.rstrip('/')}/clock/tick", json_body={"seconds": float(tick_seconds)})
                st.json(data)
            except Exception as e:
                st.error(f"Failed to tick clock: {e}")

    with c2:
        if st.button("Seek /clock/seek (0s)"):
            try:
                data = _post(f"{api_base.rstrip('/')}/clock/seek", json_body={"seconds": 0.0})
                st.json(data)
            except Exception as e:
                st.error(f"Failed to seek clock: {e}")

    with c3:
        if st.button("Fetch /replay/frame"):
            try:
                # Assumption: replay service uses current clock state to determine frame
                # and season/round are used as inputs to select dataset / metadata.
                data = _get(f"{api_base.rstrip('/')}/replay/frame?season={int(season)}&round={int(rnd)}")
                st.json(data)
            except Exception as e:
                st.error(f"Failed to fetch replay frame: {e}")

st.divider()
st.subheader("Notes")
st.markdown(
    """
- This UI is **user-driven** (no background timers).  
- Frames are fetched **on demand** from the Replay API.  
- Animation and track rendering will be added in next stories.
"""
)

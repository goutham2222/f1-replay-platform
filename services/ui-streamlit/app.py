import os
import streamlit as st
from dotenv import load_dotenv

from client.replay_api_client import ReplayApiClient

load_dotenv()

REPLAY_API_BASE_URL = os.getenv("REPLAY_API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="F1 Replay Platform", layout="wide")
st.title("F1 Replay Platform — Replay UI (Sprint 4)")

# ---------------- Session State ----------------
if "clock_state" not in st.session_state:
    st.session_state.clock_state = None

if "last_response" not in st.session_state:
    st.session_state.last_response = None

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Configuration")
    api_base = st.text_input("Replay API Base URL", REPLAY_API_BASE_URL)

    st.divider()
    st.header("Clock Controls")
    tick_ms = st.number_input(
        "Tick base_ms",
        min_value=100,
        value=1000,
        step=100,
        help="Passed directly to /clock/tick?base_ms="
    )

client = ReplayApiClient(api_base)

# ---------------- Layout ----------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Clock State")

    if st.button("Refresh /clock/state"):
        try:
            st.session_state.clock_state = client.get_clock_state()
        except Exception as e:
            st.error(str(e))

    if st.session_state.clock_state:
        st.json(st.session_state.clock_state)

with col2:
    st.subheader("Actions")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Tick /clock/tick"):
            try:
                st.session_state.last_response = client.tick_clock(tick_ms)
            except Exception as e:
                st.error(str(e))

    with c2:
        if st.button("Seek /clock/seek (0 ms)"):
            try:
                st.session_state.last_response = client.seek_clock(0)
            except Exception as e:
                st.error(str(e))

    with c3:
        if st.button("Fetch /replay/frame"):
            try:
                st.session_state.last_response = client.get_replay_frame()
            except Exception as e:
                st.error(str(e))

if st.session_state.last_response:
    st.divider()
    st.subheader("Last API Response")
    st.json(st.session_state.last_response)

st.divider()
st.subheader("Notes")
st.markdown(
    """
- UI now matches Replay API contracts exactly.
- No hidden parameters, no assumptions.
- Deterministic behavior preserved.
"""
)

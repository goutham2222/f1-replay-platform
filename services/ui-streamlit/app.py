import os
import time
import math
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from client.replay_api_client import ReplayApiClient
from client.track_geometry import load_track_geometry

# --------------------------------------------------
# Session State (MUST be first)
# --------------------------------------------------
if "auto_play" not in st.session_state:
    st.session_state.auto_play = False

if "track_df" not in st.session_state:
    st.session_state.track_df = None

# --------------------------------------------------
# Environment / Config
# --------------------------------------------------
load_dotenv()

CURATED_BUCKET = os.getenv("CURATED_BUCKET", "f1-replay-curated-goutham")
REPLAY_API_BASE_URL = os.getenv("REPLAY_API_BASE_URL", "http://localhost:8000")
TRACK_GEOMETRY_S3 = f"s3://{CURATED_BUCKET}/track_geometry/"

api = ReplayApiClient(REPLAY_API_BASE_URL)

st.set_page_config(
    page_title="F1 Replay Platform — Track Replay",
    layout="wide"
)

# --------------------------------------------------
# Utilities
# --------------------------------------------------
def interpolate_position(track_df: pd.DataFrame, lap_progress: float):
    """
    Linear interpolation between track points for smooth motion.
    """
    n = len(track_df)
    pos = lap_progress * (n - 1)

    idx0 = int(pos)
    idx1 = min(idx0 + 1, n - 1)
    t = pos - idx0

    x0, y0 = track_df.iloc[idx0][["x", "y"]]
    x1, y1 = track_df.iloc[idx1][["x", "y"]]

    x = x0 + t * (x1 - x0)
    y = y0 + t * (y1 - y0)

    return float(x), float(y)


def driver_color(driver_number: int) -> str:
    """
    Deterministic color per driver.
    """
    palette = [
        "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
        "#ff7f00", "#ffff33", "#a65628", "#f781bf",
        "#999999", "#66c2a5", "#fc8d62", "#8da0cb",
        "#e78ac3", "#a6d854", "#ffd92f"
    ]
    return palette[driver_number % len(palette)]

# --------------------------------------------------
# Sidebar — Race Configuration
# --------------------------------------------------
st.sidebar.header("Race Configuration")

season = st.sidebar.number_input("Season", 2018, 2025, 2023)
round_no = st.sidebar.number_input("Round", 1, 30, 1)

if st.sidebar.button("Load Track Geometry"):
    st.session_state.track_df = load_track_geometry(
        TRACK_GEOMETRY_S3, season, round_no
    )

# --------------------------------------------------
# Sidebar — Playback Controls
# --------------------------------------------------
st.sidebar.header("Playback Controls")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("▶ Play"):
        api._post("/clock/play")
        st.session_state.auto_play = True

    if st.button("⏭ Tick (+200ms)"):
        api.tick_clock(base_ms=200)

with col2:
    if st.button("⏸ Pause"):
        api._post("/clock/pause")
        st.session_state.auto_play = False

    if st.button("🔄 Reset"):
        api._post("/clock/reset")
        st.session_state.auto_play = False

seek_ms = st.sidebar.number_input(
    "Seek Time (ms)",
    min_value=0,
    step=1000,
    value=0
)

if st.sidebar.button("⏮ Seek"):
    api.seek_clock(seek_ms)

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("F1 Replay Platform — Track Replay")

# --------------------------------------------------
# Fetch Clock + Frame
# --------------------------------------------------
clock_state = api.get_clock_state()
frame = api.get_replay_frame()

st.caption(f"Replay Time: {clock_state['current_time_ms']} ms")

# --------------------------------------------------
# Render Track + Cars
# --------------------------------------------------
if st.session_state.track_df is not None:
    df = st.session_state.track_df

    x_centered = df["x"] - df["x"].mean()
    y_centered = df["y"] - df["y"].mean()

    fig = go.Figure()

    # Track
    fig.add_trace(
        go.Scatter(
            x=x_centered,
            y=y_centered,
            mode="lines",
            line=dict(color="white", width=4),
            hoverinfo="skip"
        )
    )

    # Cars
    cars = frame.get("driver_states", [])
    if cars:
        OFFSET_RADIUS = 0.00015
        n = len(cars)

        car_rows = []

        for i, d in enumerate(cars):
            x, y = interpolate_position(df, d["lap_progress"])

            # Visual-only radial offset
            angle = 2 * math.pi * i / n
            x += OFFSET_RADIUS * math.cos(angle)
            y += OFFSET_RADIUS * math.sin(angle)

            car_rows.append({
                "driver_number": d["driver_number"],
                "x": x - df["x"].mean(),
                "y": y - df["y"].mean(),
                "color": driver_color(d["driver_number"])
            })

        car_df = pd.DataFrame(car_rows)

        fig.add_trace(
            go.Scatter(
                x=car_df["x"],
                y=car_df["y"],
                mode="markers+text",
                marker=dict(
                    size=10,
                    color=car_df["color"]
                ),
                text=car_df["driver_number"],
                textposition="top center"
            )
        )

    fig.update_layout(
        showlegend=False,
        paper_bgcolor="black",
        plot_bgcolor="black",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_xaxes(visible=False, scaleanchor="y")
    fig.update_yaxes(visible=False)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Load track geometry to begin.")

# --------------------------------------------------
# Auto-play Loop (UI-driven)
# --------------------------------------------------
if st.session_state.auto_play:
    api.tick_clock(base_ms=200)
    time.sleep(0.05)
    st.rerun()

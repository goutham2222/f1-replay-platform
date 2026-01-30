import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pyarrow.parquet as pq
import pyarrow.fs as fs
from dotenv import load_dotenv

# --------------------------------------------------
# Environment / Config
# --------------------------------------------------
load_dotenv()

CURATED_BUCKET = os.getenv("CURATED_BUCKET", "f1-replay-curated-goutham")
TRACK_GEOMETRY_PREFIX = "track_geometry"
REPLAY_API_BASE_URL = os.getenv("REPLAY_API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="F1 Replay Platform — Track Replay",
    layout="wide"
)

# --------------------------------------------------
# Sidebar Controls
# --------------------------------------------------
st.sidebar.header("Configuration")

season = st.sidebar.number_input(
    "Season",
    min_value=2018,
    max_value=2025,
    value=2023,
    step=1
)

round_no = st.sidebar.number_input(
    "Round",
    min_value=1,
    max_value=30,
    value=1,
    step=1
)

load_track_btn = st.sidebar.button("Load Track Geometry")
fetch_frame_btn = st.sidebar.button("Fetch Replay Frame")

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("F1 Replay Platform — Track Replay")

# --------------------------------------------------
# Load Track Geometry (Parquet from S3)
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def load_track_geometry(season: int, round_no: int) -> pd.DataFrame:
    import pyarrow.dataset as ds

    dataset = ds.dataset(
        f"s3://{CURATED_BUCKET}/{TRACK_GEOMETRY_PREFIX}/",
        format="parquet",
        partitioning="hive"
    )

    table = dataset.to_table(
        filter=(
            (ds.field("season") == season)
            & (ds.field("round") == round_no)
        )
    )

    df = table.to_pandas()

    if df.empty:
        raise ValueError("No track geometry found")

    return df.sort_values("point_index").reset_index(drop=True)

# --------------------------------------------------
# Fetch Replay Frame (API)
# --------------------------------------------------
def fetch_replay_frame() -> dict:
    resp = requests.get(f"{REPLAY_API_BASE_URL}/replay/frame", timeout=10)
    resp.raise_for_status()
    return resp.json()

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "track_df" not in st.session_state:
    st.session_state.track_df = None

if "frame" not in st.session_state:
    st.session_state.frame = None

# --------------------------------------------------
# Load Track
# --------------------------------------------------
if load_track_btn:
    with st.spinner("Loading track geometry..."):
        st.session_state.track_df = load_track_geometry(season, round_no)

    st.success(f"Loaded {len(st.session_state.track_df)} track points")

# --------------------------------------------------
# Fetch Frame
# --------------------------------------------------
if fetch_frame_btn:
    with st.spinner("Fetching replay frame..."):
        st.session_state.frame = fetch_replay_frame()

# --------------------------------------------------
# Render Track + Cars
# --------------------------------------------------
if st.session_state.track_df is not None:
    df = st.session_state.track_df

    # ---- Center track ----
    x_centered = df["x"] - df["x"].mean()
    y_centered = df["y"] - df["y"].mean()

    fig = go.Figure()

    # ---- Track line ----
    fig.add_trace(
        go.Scatter(
            x=x_centered,
            y=y_centered,
            mode="lines",
            line=dict(color="white", width=4),
            hoverinfo="skip",
            name="Track"
        )
    )


    # ---- Cars (Replay Frame) ----
    if st.session_state.frame is not None:
        cars = st.session_state.frame.get("driver_states", [])

        if cars:
            car_df = pd.DataFrame(cars)

            car_x = car_df["x"] - df["x"].mean()
            car_y = car_df["y"] - df["y"].mean()

            fig.add_trace(
                go.Scatter(
                    x=car_x,
                    y=car_y,
                    mode="markers+text",
                    marker=dict(size=10, color="red"),
                    text=car_df["driver_number"],
                    textposition="top center",
                    name="Cars"
                )
            )

            st.caption(
                f"Replay time: {st.session_state.frame.get('replay_time_ms', 0)} ms"
            )

    # ---- Layout ----
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="black",
        plot_bgcolor="black",
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig.update_xaxes(visible=False, scaleanchor="y")
    fig.update_yaxes(visible=False)

    st.subheader("Track Replay")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Preview Track Data"):
        st.dataframe(df.head(20), use_container_width=True)

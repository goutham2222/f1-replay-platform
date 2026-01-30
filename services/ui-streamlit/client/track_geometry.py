import pandas as pd
import pyarrow.dataset as ds


def load_track_geometry(
    s3_path: str,
    season: int,
    round_no: int,
) -> pd.DataFrame:
    """
    Load curated track geometry directly from S3 Parquet.

    Parameters
    ----------
    s3_path : str
        Base S3 path (e.g. s3://f1-replay-curated-goutham/track_geometry/)
    season : int
    round_no : int

    Returns
    -------
    pd.DataFrame
        Ordered track points with columns: point_index, x, y
    """

    dataset = ds.dataset(
        s3_path,
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
        raise ValueError(
            f"No track geometry found for season={season}, round={round_no}"
        )

    return (
        df
        .sort_values("point_index")
        .reset_index(drop=True)
        [["point_index", "x", "y"]]
    )

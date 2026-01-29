import pyarrow.dataset as ds
import pyarrow.fs as fs
import pandas as pd


class S3PartitionNotFound(Exception):
    pass


class ParquetReader:
    def __init__(self):
        self.s3 = fs.S3FileSystem()

    def _assert_prefix_exists(self, bucket: str, prefix: str):
        """
        Ensure S3 prefix exists before attempting dataset read.
        """
        selector = fs.FileSelector(
            base_dir=f"{bucket}/{prefix}",
            allow_not_found=True,
            recursive=False,
        )

        try:
            infos = self.s3.get_file_info(selector)
        except Exception:
            raise S3PartitionNotFound(
                f"S3 prefix does not exist: s3://{bucket}/{prefix}"
            )

        if not infos:
            raise S3PartitionNotFound(
                f"S3 prefix does not exist: s3://{bucket}/{prefix}"
            )

    def read_partitioned_table(
        self,
        *,
        bucket: str,
        dataset: str,
        season: int,
        round: int | None = None,
    ) -> pd.DataFrame:
        """
        Reads curated parquet data scoped by season / round.
        """

        # ----------------------------
        # Validate partitions
        # ----------------------------
        season_prefix = f"{dataset}/season={season}"
        self._assert_prefix_exists(bucket, season_prefix)

        if round is not None:
            round_prefix = f"{season_prefix}/round={round}"
            self._assert_prefix_exists(bucket, round_prefix)
            path = f"{bucket}/{round_prefix}"
        else:
            path = f"{bucket}/{season_prefix}"

        # ----------------------------
        # Read parquet dataset
        # ----------------------------
        dataset = ds.dataset(
            path,
            filesystem=self.s3,
            format="parquet",
        )

        table = dataset.to_table()

        if table.num_rows == 0:
            raise FileNotFoundError(
                f"No parquet data found at s3://{path}"
            )

        return table.to_pandas()

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Environment
    app_env: str = Field(default="local")
    aws_region: str = Field(default="us-east-1")

    # ---- REQUIRED for Replay API ----
    curated_bucket: str = Field(
        ...,
        description="S3 bucket containing CURATED parquet data"
    )

    default_season: int = Field(
        ...,
        description="Default F1 season for replay"
    )

    default_round: int = Field(
        ...,
        description="Default race round for replay"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    curated_bucket: str = Field(
        default="f1-replay-curated-goutham"
    )
    default_season: int = Field(
        default=2023
    )
    default_round: int = Field(
        default=1
    )

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()

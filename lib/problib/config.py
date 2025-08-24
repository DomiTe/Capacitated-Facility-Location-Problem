from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Self


class ProfileConfig(BaseSettings):
    """This class is used to configure the profiling of the solver.
    It allows you to specify the directory where profiling data will be saved.
    """

    # Base directory for all data. This is the root folder where all data will be stored.
    base_data_dir: Path = Path("data")

    # Unique identifier for the profiling run. If not provided, it will be generated based on the current date and tim
    run_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    # Path to /data/profiling/{run_id}
    data_dir: Path | None = None

    # Files within the run_id subfolder
    stats_data_file: Path | None = None
    stats_txt_file: Path | None = None

    @field_validator("data_dir", mode="after")
    @classmethod
    def construct_data_dirs(cls, value: Any, info: ValidationInfo) -> Any:
        """Internally used to construct the data_dir path."""
        if not value:
            return info.data["base_data_dir"] / "profiling" / info.data["run_id"]
        return value

    @field_validator("stats_data_file", mode="after")
    @classmethod
    def construct_stats_data_file(cls, value: Any, info: ValidationInfo) -> Any:
        """Internally used to construct the stats_data_file path."""
        if not value:
            # If no file is provided, create a default one
            return info.data["data_dir"] / "stats.dat"
        return value

    @field_validator("stats_txt_file", mode="after")
    @classmethod
    def construct_stats_txt_file(cls, value: Any, info: ValidationInfo) -> Any:
        """Internally used to construct the stats_txt_file path."""
        if not value:
            return info.data["data_dir"] / "stats.txt"
        return value

    @model_validator(mode="after")
    def create_dir(self) -> Self:
        """Model validator to create the data directory if it does not exist yet."""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        return self

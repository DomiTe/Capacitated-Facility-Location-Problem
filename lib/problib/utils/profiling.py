from snakeviz.cli import main as snakeviz_main

from problib.config import ProfileConfig
from problib.log import log


def visualize_profiler_results(profiler_config: ProfileConfig) -> None:
    """Visualize the profiling data using snakeviz.

    Args:
        profiler_config (ProfileConfig): Configuration for profiling.
    """

    log.info(f"Visualizing profiling data for run_id: '{profiler_config.run_id}'")
    if not profiler_config.data_dir.exists():
        log.error(f"Profiling data directory not found: '{profiler_config.data_dir}'")
        return
    if not profiler_config.stats_data_file.exists():
        log.error(f"Profiling data file not found: '{profiler_config.stats_data_file}'")
        return
    log.info("Visualizing profiling data.")
    snakeviz_main([f"{str(profiler_config.stats_data_file)}", "-s"])

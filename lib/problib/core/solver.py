import cProfile
import pstats
from abc import ABC, abstractmethod

from problib.config import ProfileConfig
from problib.log import log
from problib.utils.profiling import visualize_profiler_results


class BaseSolver(ABC):
    """This is the base class for all solvers.
    It provides a common interface for solving problems and profiling the solution process.
    The class is designed to be subclassed by specific solver implementations.
    """

    def __init__(self, profile_config: ProfileConfig | None = None, *args, **kwargs):
        log.info(f"Initializing {self.name} solver")
        self.args = args
        self.kwargs = kwargs
        self.profiler_config = profile_config or ProfileConfig()

    def run(self, profile: bool = False, *args, **kwargs) -> None:
        """Main entry point for solving the problem.
        This method can be used to enable profiling for performance analysis.
        This method will call the `_solve` method, which should be implemented
        by subclasses and holds the actual logic for solving the problem.

        Per default, the profiling data will be saved in the 'projects/<>/data/profiling' directory
        with a subfolder named after the current date and time (format: YYYYMMDD_HHMMSS).
        The profiling data will be saved in two files:
        - stats.dat: Contains the profiling data in a binary format.
        - stats.txt: Contains the profiling data in a human-readable format.

        Args:
            profile (bool, optional): Use profiler. Defaults to False.
        """
        if profile:
            log.info("Solving with profiling enabled.")
            cProfile.runctx(
                "self._solve()",
                globals=globals(),
                locals=locals(),
                filename=self.profiler_config.stats_data_file,
            )
            with open(self.profiler_config.stats_txt_file, "w") as f:
                ps = pstats.Stats(str(self.profiler_config.stats_data_file), stream=f)
                ps.sort_stats("cumulative")
                ps.print_stats()
            log.info(
                "Profiling data saved",
                raw_stats=self.profiler_config.stats_data_file,
                txt_stats=self.profiler_config.stats_txt_file,
            )

            return

        log.info("Solving without profiling.")
        self._solve(*args, **kwargs)

    @abstractmethod
    def _solve(self, *args, **kwargs) -> None:
        """Abstract method to be implemented by subclasses for solving the problem.
        This method should **only** contain the logic for solving the problem.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """

        raise NotImplementedError(
            f"Solver '{self.name()}' does not implement the '_solve' method."
        )

    def visualize_profile(self) -> None:
        """Visualize the profiling data.
        This method can be used to visualize the profiling data generated during the solving process.
        """
        log.info("Visualizing profiling data.")
        visualize_profiler_results(self.profiler_config)

    def name(self) -> str:
        """Return the name of the solver.

        Returns:
            str: The name of the solver.
        """
        return self.__class__.__name__

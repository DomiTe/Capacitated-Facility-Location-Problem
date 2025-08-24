import os

import osmnx as ox
from problib import BaseSolver
from problib.io.file import read_json
from problib.log import log

from facility_location.conf import config
from facility_location.helper.cost_util import _write_and_save_cost_matrix
from facility_location.helper.data_extraction_cflp import generate_city_data
from facility_location.helper.solver_util import (
    _load_and_handle_gdf,
    solve_capacitated_flp,
)


class FacilityLocationSolver(BaseSolver):
    def __init__(self, project_data_path: str = "data"):
        super().__init__()
        self.project_data_path = project_data_path

        # Initialize data containers
        self.practitioners_gdf = None
        self.pharmacies_gdf = None
        self.facility_capacities: dict = {}
        self.demand_quantities: dict = {}
        self.city_boundary = None
        self.cost_matrix = None  # Distance in Meters

        # Model result parameters
        self.open_facilities = []
        self.assignments = {}
        self.solving_time: float = 0.0

        # Configure OSMnx for geocoding and caching
        ox.settings.log_console = True
        ox.settings.use_cache = True

    def load_data(self):
        """
        Loads all necessary data from geojson files.

        This method orchestrates the entire data preparation pipeline, including:
        - Fetching the geographical boundary of the city used in config
        - Loading facility and demand point locations
        - Processing IDs and assigning capacities/demands
        - Loading or computing the cost matrix
        """

        # Ensure data directory exists; creates it if it doesn't
        os.makedirs(self.project_data_path, exist_ok=True)

        city_name = config.city
        city_filename_prefix = city_name.split(",")[0].lower().replace(" ", "_")
        log.info(f"Starting data loading process for {city_name.upper()}")

        practitioners_file = f"{city_filename_prefix}_practitioners.geojson"
        pharmacies_file = f"{city_filename_prefix}_pharmacies.geojson"
        practitioners_path = os.path.join(self.project_data_path, practitioners_file)
        pharmacies_path = os.path.join(self.project_data_path, pharmacies_file)

        if not os.path.exists(practitioners_path) or not os.path.exists(
            pharmacies_path
        ):
            log.info(f"Data for {city_name} not found. Generating from OpenStreetMap")
            generate_city_data(city_name, self.project_data_path)
        try:
            self.city_boundary = ox.geocode_to_gdf(city_name)
        except Exception as e:
            log.error(f"Could not fetch boundary for {city_name}. Error:{e}")
            return

        # Load pharmacy data. The helper function attempts to load from a GeoJSON file.
        self.pharmacies_gdf = _load_and_handle_gdf(
            self.project_data_path,
            pharmacies_file,  # The file to look for.
            "pharmacies",  # A name for logging/identification.
        )

        # Load practitioner data using the same logic as for pharmacies.
        self.practitioners_gdf = _load_and_handle_gdf(
            self.project_data_path,
            practitioners_file,  # The file to look for.
            "practitioners",  # A name for logging/identification.
        )

        # --- Process Pharmacy Data ---
        # This block ensures pharmacies have a consistent string-based ID and a defined capacity.
        if self.pharmacies_gdf is not None and not self.pharmacies_gdf.empty:
            # Create a 'string_id' column. Solvers often work best with string keys.
            # Use the existing 'id' column if available; otherwise, use the GeoDataFrame index.
            if "id" in self.pharmacies_gdf.columns:
                self.pharmacies_gdf["string_id"] = self.pharmacies_gdf["id"].astype(str)
            else:
                self.pharmacies_gdf["string_id"] = self.pharmacies_gdf.index.astype(str)

            # Assign a fixed capacity to each pharmacy. Here, every pharmacy can serve 5 practitioners.
            # In a real-world scenario, this could be based on staff size, hours, etc.
            self.pharmacies_gdf["capacity"] = config.pharmacy_capacity
            self.facility_capacities = dict(
                zip(self.pharmacies_gdf["string_id"], self.pharmacies_gdf["capacity"])
            )

        # --- Process Practitioner Data ---
        # This block ensures practitioners have a string ID and a defined demand quantity.
        if self.practitioners_gdf is not None and not self.practitioners_gdf.empty:
            # Create a 'string_id' column, similar to the pharmacy processing step.
            if "id" in self.practitioners_gdf.columns:
                self.practitioners_gdf["string_id"] = self.practitioners_gdf[
                    "id"
                ].astype(str)
            else:
                self.practitioners_gdf["string_id"] = (
                    self.practitioners_gdf.index.astype(str)
                )
            # Assign a uniform demand to each practitioner. Each demand point is a single entity to be served.
            self.demand_quantities = {
                gp_id: config.practitioner_demand
                for gp_id in self.practitioners_gdf["string_id"]
            }

        # --- Load or Compute the Cost Matrix ---
        # The cost matrix is often the most time-consuming part to generate. This logic
        # avoids re-computation by saving it to a file.
        cost_matrix_path = os.path.join(
            self.project_data_path, f"cost_matrix_{city_filename_prefix}.json"
        )

        if os.path.exists(cost_matrix_path):
            # If the cost matrix file exists, try to load it.
            self.cost_matrix = read_json(cost_matrix_path)
            if not self.cost_matrix:
                # If loading fails (e.g., file is empty or corrupt), `read_json` might return None or an empty dict.
                self.cost_matrix = _write_and_save_cost_matrix(
                    self.project_data_path,
                    cost_matrix_path,
                    self.practitioners_gdf,
                    self.pharmacies_gdf,
                )
        else:
            # If the cost matrix file does not exist, compute it from scratch and save it for future use.
            self.cost_matrix = _write_and_save_cost_matrix(
                self.project_data_path,
                cost_matrix_path,
                self.practitioners_gdf,
                self.pharmacies_gdf,
            )

    def _solve(self):
        """
        Executes the capacitated facility location problem solver.

        This method is intended for internal use.
        It takes the pre-processed data and feeds it into the optimizer.
        """
        # --- Pre-computation Check ---
        # A guard clause to ensure that all required data components are available.
        # If any data is missing, the solver cannot run, so we exit.
        if (
            not self.cost_matrix
            or not self.facility_capacities
            or not self.demand_quantities
        ):
            self.open_facilities = []
            self.assignments = {}
            self.solving_time = 0
            return

        # --- Run the Solver ---
        # Call the external solver function with all the prepared data and parameters.
        # This function contains the core mathematical optimization model.
        self.open_facilities, self.assignments, self.solving_time = (
            solve_capacitated_flp(
                self.cost_matrix,
                facility_capacities=self.facility_capacities,
                demand_quantities=self.demand_quantities,
            )
        )

    def get_results(self) -> tuple[list, dict, float]:
        """
        Provides a clean, public interface to access the results of the solver.

        Returns:
            A tuple containing:
            - list: The IDs of the facilities selected to be opened.
            - dict: A mapping of demand points to their assigned open facility.
            - float: The time taken by the solver to find the solution.
        """
        return self.open_facilities, self.assignments, self.solving_time

import json
import math
import os
import time

import geopandas as gpd
import numpy as np
from facility_location.conf import config
from problib.log import log
from pyscipopt import Model, quicksum
from shapely.geometry import Point

# This file contains helper functions for:
# - JSON serialization of NumPy data types (NpEncoder class)
# - Creating dummy GeoDataFrames for pharmacies and practitioners
# - Loading GeoDataFrames from files or generating dummy data if files are not found (_load_and_handle_gdf)
# - Solving the Capacitated Facility Location Problem (CFLP) using PySCIPOpt


class NpEncoder(json.JSONEncoder):
    """
    JSON encoder to handle NumPy types for serialization.
    Inherits from json.JSONEncoder and overrides the default method.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def create_dummy_pharmacy_data() -> gpd.GeoDataFrame:
    """Creates a dummy GeoDataFrame of pharmacies."""
    dummy_data = {
        "name": [f"Dummy_Pharmacy_{i}" for i in range(10)],
        "geometry": [Point(13.4 + 0.01 * i, 52.5 + 0.005 * i) for i in range(10)],
    }
    return gpd.GeoDataFrame(dummy_data, crs="EPSG:32633")


def create_dummy_prac_data() -> gpd.GeoDataFrame:
    """Creates a dummy GeoDataFrame of practitioners."""
    dummy_data = {
        "name": [f"Dummy_Practitioner_{i}" for i in range(10)],
        "geometry": [Point(13.35 + 0.02 * i, 52.51 + 0.005 * i) for i in range(10)],
    }
    return gpd.GeoDataFrame(dummy_data, crs="EPSG:32633")


def get_utm_epsg(gdf: gpd.GeoDataFrame) -> str:
    """
    Automatically determines the correct UTM EPSG code for a given GeoDataFrame.

    UTM (Universal Transverse Mercator) is a coordinate system that projects the
    Earth onto a 2D surface, using meters for units. This is ideal for accurate
    distance calculations. This function finds the geographic center of the data
    to determine the correct UTM zone.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame with geographic data.

    Returns:
        str: The appropriate UTM EPSG code as a string (e.g., "EPSG:32633").
    """
    # Ensure CRS is WGS 84 (EPSG:4326) for lat/lon calculations.
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")
    # Find the geographic center of all combined geometries.
    centroid = gdf.geometry.unary_union.centroid
    # Get longitude and latitude from the centroid.
    longitude = centroid.x
    latitude = centroid.y
    # Calculate the UTM zone number (1-60) from the longitude.
    utm_zone = math.floor((longitude + 100) / 6) + 1
    # Select the EPSG base code based on the hemisphere.
    if latitude >= 0:
        # Construct EPSG code for the Northern Hemisphere (base 326xx).
        epsg_code = f"EPSG:326{utm_zone:02d}"
    else:
        # Construct EPSG code for the Southern Hemisphere (base 327xx).
        epsg_code = f"EPSG:327{utm_zone:02d}"
    return epsg_code


def _load_and_handle_gdf(
    project_data_path,
    file_name,
    data_description,
):
    """
    Helper method to load GeoDataFrames or create dummy data if files are not found.
    Args:
        project_data_path (str): The path to the project's data directory.
        file_name (str): The name of the GeoJSON file.
        data_description (str): A description of the data (e.g., "pharmacies").
    Returns:
        geopandas.GeoDataFrame: The loaded or created GeoDataFrame.
    """
    file_path = os.path.join(project_data_path, file_name)
    gdf = None
    if os.path.exists(file_path):
        try:
            gdf = gpd.read_file(file_path)
            log.info(f"Loaded {data_description} data from {file_path}")
        except Exception as e:
            log.info(f"Error loading {data_description} from {file_path}: {e}")
    else:
        log.info(f"Data file not found: {file_path}. Please ensure the file exists.")

    if gdf is None or gdf.empty:
        log.info(f"No {data_description} data loaded.")

    return gdf


def solve_capacitated_flp(
    cost_matrix: dict,
    facility_capacities: dict,
    demand_quantities: dict,
    fixcost: float = None,
    time_limit: int = 600,
) -> tuple[list, dict, float]:
    """
    Solves the Capacitated Facility Location Problem using PySCIPOpt.
    """
    log.info("\nSolving Facility Location Problem with PySCIPOpt...")

    # Use the passed fixcost of unittetsts if available, otherwise fall back to the config file.
    if fixcost is None:
        fixcost = config.fix_cost

    model = Model("flp")

    # Sets
    demand_points_ids = list(cost_matrix.keys())
    facilities_ids = list({f_id for d in cost_matrix.values() for f_id in d})

    if not demand_points_ids or not facilities_ids:
        log.info("No demand points or facilities found. Exiting.")
        return [], {}, 0.0

    for d_id in demand_points_ids:
        if d_id not in demand_quantities:
            raise ValueError(f"Missing demand quantity for '{d_id}'")
    for f_id in facilities_ids:
        if f_id not in facility_capacities:
            raise ValueError(f"Missing capacity for facility '{f_id}'")

    # Variables
    x = {
        (d_id, f_id): model.addVar(vtype="B", name=f"x_{d_id}_{f_id}")
        for d_id in demand_points_ids
        for f_id in facilities_ids
    }
    y = {f_id: model.addVar(vtype="B", name=f"y_{f_id}") for f_id in facilities_ids}

    # Objective
    model.setObjective(
        quicksum(
            cost_matrix[d_id].get(f_id, 1e9) * demand_quantities[d_id] * x[(d_id, f_id)]
            for d_id in demand_points_ids
            for f_id in facilities_ids
        )
        + quicksum(fixcost * y[f_id] for f_id in facilities_ids),
        "minimize",
    )

    # Constraints
    for d_id in demand_points_ids:
        model.addCons(quicksum(x[(d_id, f_id)] for f_id in facilities_ids) == 1)

    for d_id in demand_points_ids:
        for f_id in facilities_ids:
            model.addCons(x[(d_id, f_id)] <= y[f_id])

    for f_id in facilities_ids:
        model.addCons(
            quicksum(
                demand_quantities[d_id] * x[(d_id, f_id)] for d_id in demand_points_ids
            )
            <= facility_capacities[f_id] * y[f_id]
        )

    model.setParam("limits/time", config.mip_time_limit)
    model.setParam("limits/gap", config.mip_gap_limit)

    log.info("Starting optimization...")
    start_time = time.time()
    model.optimize()
    end_time = time.time()
    solving_time = end_time - start_time

    open_facilities = []
    assignments = {}
    total_assignment_cost = 0
    facility_loads = {f_id: 0.0 for f_id in facilities_ids}

    if model.getStatus() in ["optimal", "timelimit"]:
        log.info(f"\nStatus: {model.getStatus()} | Total Cost: {model.getObjVal():.2f}")

        for f_id in facilities_ids:
            if model.getVal(y[f_id]) > 0.5:
                open_facilities.append(f_id)

        for d_id in demand_points_ids:
            for f_id in facilities_ids:
                if model.getVal(x[(d_id, f_id)]) > 0.5:
                    assignments[d_id] = f_id
                    total_assignment_cost += (
                        cost_matrix[d_id].get(f_id, 1e9) * demand_quantities[d_id]
                    )
                    facility_loads[f_id] += demand_quantities[d_id]
                    break

        log.info(f"Total Assignment Cost: {total_assignment_cost:.2f}")
        log.info(f"Total Opening Cost: {len(open_facilities) * fixcost:.2f}")

        # Save assignments
        city_name = config.city
        city_filename_prefix = city_name.split(",")[0].lower().replace(" ", "_")
        assignment_results_path = f"data/cflp_assignments_{city_filename_prefix}.json"
        try:
            os.makedirs(os.path.dirname(assignment_results_path), exist_ok=True)
            with open(assignment_results_path, "w") as f:
                json.dump(assignments, f, indent=2, cls=NpEncoder)
            log.info(f"\nAssignments saved to {assignment_results_path}")
        except Exception as e:
            log.info(f"Error saving results: {e}")

        return open_facilities, assignments, solving_time
    else:
        log.info(f"\nModel status: {model.getStatus()}. No feasible solution found.")
        return [], {}, solving_time

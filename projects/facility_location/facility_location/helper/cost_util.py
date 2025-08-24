import geopandas as gpd
import numpy as np
from facility_location.helper.solver_util import get_utm_epsg
from problib.io.file import write_json
from problib.log import log
from scipy.spatial.distance import cdist
from shapely.geometry import MultiPolygon, Point, Polygon


def calculate_cost_matrix(
    demand_gdf: gpd.GeoDataFrame, facilities_gdf: gpd.GeoDataFrame
) -> dict:
    """
    Calculates a dummy cost matrix (Euclidean distance) between demand points and facilities.
    """
    log.info("Executing calculate_cost_matrix function...")

    # Return empty if either input is empty
    if demand_gdf.empty or facilities_gdf.empty:
        log.info(
            "One of the input GeoDataFrames is empty, returning empty cost matrix."
        )
        return {}

    # Check for required ID columns
    if "string_id" not in demand_gdf.columns:
        raise ValueError("demand_gdf must have a 'string_id' column.")
    if "string_id" not in facilities_gdf.columns:
        raise ValueError("facilities_gdf must have a 'string_id' column.")

    # Helper to extract point coordinates or polygon centroids
    def get_point_coords(geometry):
        if isinstance(geometry, Point):
            return geometry.x, geometry.y
        elif isinstance(geometry, (Polygon, MultiPolygon)):
            if geometry.is_valid and not geometry.is_empty:
                centroid = geometry.centroid
                return centroid.x, centroid.y
            else:
                log.info(f"Warning: Invalid/empty Polygon found: {geometry}")
                return None, None
        else:
            log.info(f"Warning: Unexpected geometry type: {type(geometry)}")
            return None, None

    # Use UTM Zone for accurate distance calculations in meters
    target_proj_crs = get_utm_epsg(demand_gdf)
    try:
        demand_gdf_proj = demand_gdf.to_crs(target_proj_crs)
        facilities_gdf_proj = facilities_gdf.to_crs(target_proj_crs)
        log.info(f"Reprojected GeoDataFrames to {target_proj_crs}")
    except Exception as e:
        log.info(f"Warning: Reprojection failed. Using original CRS. Error: {e}")
        demand_gdf_proj = demand_gdf
        facilities_gdf_proj = facilities_gdf

    # Extract coordinates from demand geometries
    demand_coords_list = []
    demand_ids_for_matrix = []
    for idx, geom in zip(demand_gdf_proj["string_id"], demand_gdf_proj.geometry):
        coords = get_point_coords(geom)
        if coords[0] is not None:
            demand_coords_list.append(coords)
            demand_ids_for_matrix.append(str(idx))

    # Extract coordinates from facility geometries
    facilities_coords_list = []
    facility_ids_for_matrix = []
    for idx, geom in zip(
        facilities_gdf_proj["string_id"], facilities_gdf_proj.geometry
    ):
        coords = get_point_coords(geom)
        if coords[0] is not None:
            facilities_coords_list.append(coords)
            facility_ids_for_matrix.append(str(idx))

    # Exit early if no valid coordinates
    if not demand_coords_list or not facilities_coords_list:
        log.info("No valid geometries found. Cannot calculate cost matrix.")
        return {}

    # Convert lists to numpy arrays and calculate Euclidean distances
    demand_coords = np.array(demand_coords_list)
    facilities_coords = np.array(facilities_coords_list)
    distances = cdist(demand_coords, facilities_coords, "euclidean")

    # Build nested dictionary cost matrix
    cost_matrix = {}
    for i, demand_id_str in enumerate(demand_ids_for_matrix):
        cost_matrix[demand_id_str] = {}
        for j, facility_id_str in enumerate(facility_ids_for_matrix):
            cost_matrix[demand_id_str][facility_id_str] = distances[i, j]

    log.info("Cost matrix calculated.")
    return cost_matrix


def _write_and_save_cost_matrix(
    project_data_path, cost_matrix_path, practitioners_gdf, pharmacies_gdf
):
    """
    Calculates and saves the cost matrix as a JSON file.
    """
    log.info("Calculating travel cost matrix...")

    # Sanity check for input data
    if practitioners_gdf.empty or pharmacies_gdf.empty:
        log.info("Cannot calculate cost matrix: GP or Pharmacy data is missing.")
        return {}

    # Compute cost matrix using the utility function above
    calculated_matrix = calculate_cost_matrix(practitioners_gdf, pharmacies_gdf)

    # Save if calculation succeeded
    if calculated_matrix:
        write_json(cost_matrix_path, calculated_matrix)
        log.info(f"Cost matrix saved to {cost_matrix_path}")
    else:
        log.info("Could not calculate cost matrix.")

    return calculated_matrix

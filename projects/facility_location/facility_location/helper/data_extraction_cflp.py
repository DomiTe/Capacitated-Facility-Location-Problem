import os

import geopandas as gpd
import osmnx as ox
from problib.log import log


def _unify_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Ensures all geometries are Points. Converts Polygons/MultiPolygons to their centroids.
    """
    # Create a copy to avoid SettingWithCopyWarning
    gdf_copy = gdf.copy()

    # Identify geometries that are not Points
    non_point_mask = ~gdf_copy.geometry.type.isin(["Point"])

    if non_point_mask.any():
        log.info(
            f"Found {non_point_mask.sum()} non-Point geometries (e.g., Polygons). Converting to centroids."
        )
        # Replace the geometry of non-Point features with their centroid
        gdf_copy.loc[non_point_mask, "geometry"] = gdf_copy.loc[
            non_point_mask, "geometry"
        ].centroid

    return gdf_copy


def fetch_and_clean_practitioners(place_name: str) -> gpd.GeoDataFrame:
    """
    Fetches practitioner data for a given place from OpenStreetMap,
    cleans it, and filters out unwanted categories.

    Args:
        place_name (str): The name of the place to query (e.g., "Berlin, Germany" or "Sydney, Australia").

    Returns:
        gpd.GeoDataFrame: A cleaned GeoDataFrame of practitioners.
    """
    log.info(f"--- Starting practitioner data fetch for '{place_name}' ---")

    # Broadly fetch all potential medical amenities
    tags = {"amenity": ["doctors", "dentist", "veterinary"], "healthcare": "doctor"}

    try:
        practitioners_gdf = ox.features_from_place(place_name, tags)
        log.info(
            f"Initial fetch: Found {len(practitioners_gdf)} potential medical amenities."
        )
    except Exception as e:
        log.info(f"Could not fetch data from OSMnx. Error: {e}")
        return gpd.GeoDataFrame()

    # --- Unifying Geometries to handle errors in data extraction (points and polygons) ---
    practitioners_gdf = _unify_geometries(practitioners_gdf)

    # --- Data Cleaning and Filtering ---
    # Filter out excluded practitioner types (hospitals, dentists, vets)
    original_count = len(practitioners_gdf)
    practitioners_gdf = practitioners_gdf[
        ~practitioners_gdf["amenity"].isin(["hospital", "dentist", "veterinary"])
    ]
    if len(practitioners_gdf) < original_count:
        log.info(
            f"Filtered: Removed {original_count - len(practitioners_gdf)} excluded types (hospitals, dentists, vets)."
        )

    # Select and rename useful columns
    columns_map = {
        "name": "name",
        "geometry": "geometry",
        "amenity": "amenity",
        "healthcare": "healthcare_type",
        "healthcare:speciality": "speciality",
    }
    columns_to_keep = [
        col for col in columns_map.keys() if col in practitioners_gdf.columns
    ]
    final_gdf = practitioners_gdf[columns_to_keep].rename(columns=columns_map)

    # Remove all rows with any NaN values (e.g., missing name or geometry)
    original_count = len(final_gdf)
    final_gdf.dropna(inplace=True)
    if len(final_gdf) < original_count:
        log.info(
            f"Cleaned: Removed {original_count - len(final_gdf)} entries with any missing data (NaN)."
        )

    # Remove duplicates based on name and location
    original_count = len(final_gdf)
    final_gdf = final_gdf.drop_duplicates(subset=["name", "geometry"])
    if len(final_gdf) < original_count:
        log.info(
            f"Cleaned: Removed {original_count - len(final_gdf)} duplicate entries."
        )

    log.info("\n--- Practitioner Processing Complete ---")
    log.info(
        f"Found {len(final_gdf)} cleaned and filtered practitioners in {place_name}."
    )

    return final_gdf


def fetch_and_clean_pharmacies(place_name: str) -> gpd.GeoDataFrame:
    """
    Fetches pharmacy data for a given place from OpenStreetMap and cleans it.

    Args:
        place_name (str): The name of the place to query (e.g., "Berlin, Germany" or "Munich, Germany").

    Returns:
        gpd.GeoDataFrame: A cleaned GeoDataFrame of pharmacies.
    """
    log.info(f"\n--- Starting pharmacy data fetch for '{place_name}' ---")

    # Fetch all features tagged as pharmacies
    tags = {"amenity": "pharmacy"}

    try:
        pharmacies_gdf = ox.features_from_place(place_name, tags)
        log.info(f"Initial fetch: Found {len(pharmacies_gdf)} potential pharmacies.")
    except Exception as e:
        log.info(f"Could not fetch data from OSMnx. Error: {e}")
        return gpd.GeoDataFrame()

    # --- Unifying Geometries to handle errors in data extraction (points and polygons) ---
    pharmacies_gdf = _unify_geometries(pharmacies_gdf)

    # --- Data Cleaning and Filtering ---
    # Select and rename useful columns
    columns_map = {
        "name": "name",
        "geometry": "geometry",
        "amenity": "amenity",
        "dispensing": "dispensing",
    }
    columns_to_keep = [
        col for col in columns_map.keys() if col in pharmacies_gdf.columns
    ]
    final_gdf = pharmacies_gdf[columns_to_keep].rename(columns=columns_map)

    # Remove all rows with any NaN values (e.g., missing name or geometry)
    original_count = len(final_gdf)
    final_gdf.dropna(inplace=True)
    if len(final_gdf) < original_count:
        log.info(
            f"Cleaned: Removed {original_count - len(final_gdf)} entries with any missing data (NaN)."
        )

    # Remove duplicates based on name and location
    original_count = len(final_gdf)
    final_gdf = final_gdf.drop_duplicates(subset=["name", "geometry"])
    if len(final_gdf) < original_count:
        log.info(
            f"Cleaned: Removed {original_count - len(final_gdf)} duplicate entries."
        )

    log.info("\n--- Pharmacy Processing Complete ---")
    log.info(f"Found {len(final_gdf)} cleaned pharmacies in {place_name}.")

    return final_gdf


def generate_city_data(city_name: str, output_dir: str = "data"):
    """
    Orchestrates fetching, cleaning, and saving practitioner and pharmacy data for a given city.

    This function acts as a high-level controller that calls other, more specific functions
    to perform the detailed steps of data acquisition and processing.

    Args:
        city_name (str): The name of the city to query (e.g., "Berlin, Germany").
        output_dir (str): The directory where the final GeoJSON files will be saved.
                            Defaults to a 'data' subdirectory.
    """
    # Log an informational message to indicate the start of the process for a specific city.
    log.info(f"Generating data for city: {city_name.upper()}")
    os.makedirs(output_dir, exist_ok=True)

    # --- Data Processing for Practitioners ---
    city_filename_prefix = city_name.split(",")[0].lower().replace(" ", "_")
    # Call a separate function to handle the fetching and cleaning of practitioner data.
    practitioners = fetch_and_clean_practitioners(city_name)
    # Check if the returned GeoDataFrame actually contains any data.
    if not practitioners.empty:
        output_filename = os.path.join(
            output_dir, f"{city_filename_prefix}_practitioners.geojson"
        )
        # Save the cleaned practitioner data to a GeoJSON file.
        practitioners.to_file(output_filename, driver="GeoJSON")
        log.info(f"\nCleaned practitioner data saved to {output_filename}")
    else:
        log.info(f"\nNo practitioner data found for {city_name}")

    # --- Data Processing for Pharmacies ---
    # The same process is now repeated for the pharmacy data.
    pharmacies = fetch_and_clean_pharmacies(city_name)

    # Check if any pharmacy data was returned.
    if not pharmacies.empty:
        output_filename = os.path.join(
            output_dir, f"{city_filename_prefix}_pharmacies.geojson"
        )
        # Save the cleaned pharmacy data to a GeoJSON file.
        pharmacies.to_file(output_filename, driver="GeoJSON")
        log.info(f"\nCleaned pharmacies data saved to {output_filename}")
    else:
        log.info(f"\nNo pharmacies data found for {city_name}")

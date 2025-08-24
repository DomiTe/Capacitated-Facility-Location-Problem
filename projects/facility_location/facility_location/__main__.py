import os

from problib.log import log

from facility_location.conf import config
from facility_location.helper.visualisation_util import (
    plot_optimized_facility_assignments,
)
from facility_location.solver import FacilityLocationSolver


def main():
    solver = FacilityLocationSolver()

    # Load data
    solver.load_data()

    # Run the solver (with profiling if enabled)
    solver.run(profile=True)

    # Retrieve results
    open_facilities, assignments, solving_time = solver.get_results()
    log.info(f"\nTotal problem solving time: {solving_time:.4f} seconds")

    # Get relevant GeoDataFrames for visualization
    practitioners_gdf = solver.practitioners_gdf
    pharmacies_gdf = solver.pharmacies_gdf
    city_boundary = solver.city_boundary

    # Ensure output directory exists
    output_dir = "maps"
    os.makedirs(output_dir, exist_ok=True)

    city_name = config.city
    city_filename_prefix = city_name.split(",")[0].lower().replace(" ", "_")

    output_map_path = os.path.join(
        output_dir, f"cflp_results_{city_filename_prefix}.html"
    )

    # Generate visualization map if results exist
    if open_facilities and assignments:
        try:
            plot_optimized_facility_assignments(
                practitioners_gdf=practitioners_gdf,
                pharmacies_gdf=pharmacies_gdf,
                boundary_gdf=city_boundary,
                open_facilities=set(open_facilities),
                assignments=assignments,
                output_path=output_map_path,
            )
            log.info(f"Map saved to {output_map_path}")
        except Exception as e:
            log.info(f"Map generation failed: {e}")
    else:
        log.info("No results to visualize. Skipping map generation.")


if __name__ == "__main__":
    main()

# (Capacitated) Facility Location Project

This project is designed to solve the *Capacitated Facility Location Problem (CFLP)* for assigning practitioners to optimal pharmacy locations of a City of your choice. The main goal is to select a subset of pharmacy locations that minimizes the total cost (in Euros) of assigning each Practitioner to one pharmacy.

---

## Features

- Load or generate geospatial data for pharmacies and practitioners for a city named in the config file.
- Assigning each pharmacy a fixed capacity of 5 and each practitioner a uniform demand of 1
- Calculate a cost matrix using geographic distances between practitioners and pharmacies.
- Solve the CFLP using Mixed Integer Programming via PySCIPOpt.
- Visualize the initial and optimized facility assignments on interactive Folium maps.
- Modular structure for data handling, optimization, and visualization.

---

## Project Structur
```
facility_location/
├── data/
│   ├── berlin_pharmacies.geojson
│   ├── berlin_practitioners.geojson
│   ├── cflp_assignments_berlin.json
│   └── cost_matrix_berlin.json
├── facility_location/
│   ├── __init__.py
│   ├── __main__.py
│   ├──solver.py
|   └── helper/
│       ├── cost_util.py
│       ├── solver_util.py
│       ├── data_extraction_clfp.py
│       └── visualisation_util.py
├── maps/
│   ├── cflp_results_berlin.html
│   ├── cflp_results_potsdam.html
│   ├── cflp_results_seoul.html
│   └── cflp_results_sydney.html
├── tests/
│   └── test_cflp_solver.py
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```
---

## Installation

Install the project's dependencies using `uv` from within this project's directory root:

```bash
# /projects/facility_location
uv sync
```

---

## Basic Usage

Run every command from the root of this project directory: `/projects/facility_location`.

This is important because the project uses relative imports and expects to be run from its root directory.
Run this project by calling the main module's entrypoint.

This will:

* Load the data,
* Compute the cost matrix,
* Solve the optimization model,
* Save the results.

To execute the optimization workflow, run:

```bash
uv run python -m facility_location
```

This will trigger the main solver, perform the optimization, and save the resulting assignments to a JSON file in `data/`.

---

## Visualization

A result map will be automatically created (saved as `.html`), and can be opened in any browser

### Plot optimized assignments after solving:

```python
from helper.visualisation_util import plot_optimized_facility_assignments
```

---
## Dataset

The provided dataset consists of:

* A boundary polygon for a city fetched via OSMnx.
* GeoJSON files (fetched via OSMnx) for:

  * **Pharmacies** (`berlin_pharmacies.geojson`)
  * **Practitioners** (`berlin_practitioners.geojson`)

Both Datasets have been generated using:

  * `data_extraction_cflp.py`

Execute the following command to generate the *pharmacy and *practitioners data for another city:

```bash
uv run facility_location/helper/data_extraction_cflp.py
```


This Skript will extract all pharmacies and all practitioners of any other city given as input in the config file or thte .env-file and clean these datasets off of NaN-entries and duplicates. Additionally, in the practitioner dataset all hospitals, dentists and veterinary have been excluded.

### Handling of Datasets

Additionally to correctly handle the calculation for the cost matrix, for both datasets, coordinates are projected via `crs`. The reason for this is to take the spherical latitude and longitude coordinates in both GEOjson files into account. Projecting these coordinates onto a 2D Map according to the suitable UTM-zone. This ensures realistic calculations for the euclidean distance.

### Structure of Datasets

Each location includes attributes such as:

* `name`
* `geometry` (Shapely Point)
* `string_id` (used as a unique reference in the solver)

## Configuration

This project is _partially_ configured with pydantic [BaseSettings](https://docs.pydantic.dev/latest/concepts/pydantic_settings).

Configuration parameters have to be set in the .env file. As a reference file, see .env_copy.

## Experiment

The project includes an optimization experiment using PySCIPOpt to compare cost-effective pharmacy placement. The solver minimizes total travel cost (distance) from Practitioners to assigned pharmacies, while also considering not only fixed costs for opening each pharmacy but also the capacity of each pharmacy.

To run the optimization, use:

```python
from facility_location.solver import FacilityLocationSolver

solver = FacilityLocationSolver()
solver.load_data()
solver.run()

open_facilities, assignments, solving_time = solver.get_results()
```

The assignment results will be saved as:

```text
data/cflp_assignments_berlin.json
```

These results can be used for further spatial analysis or reporting.

## Testing

This project includes a suite of unit tests to ensure the correctness and robustness of the `solve_capacitated_flp` function and related logic.

### Running Tests

To run the tests, navigate to the **root of this project directory** (`/projects/facility_location`) and execute the following command using `uv`:

```bash
uv run python -m unittest tests/test_cflp_solver.py
```

This command will:

1.  Activate the project's `uv`-managed virtual environment.
2.  Execute the `unittest` module, specifically running the tests defined in `tests/test_flp_solver.py`.


### Test Details

The tests cover various scenarios, including:

  * **Basic Functionality:** Verification that the solver correctly identifies the optimal facility locations and assignments for small, manually verifiable problem instances.
  * **Edge Cases:** Handling of empty input data (e.g., no demand points or no facilities).
  * **Cost Sensitivity:** Tests to ensure the solver behaves as expected under extreme conditions, such as very high or very low facility opening costs.
  * **GeoDataFrame Usage:** Tests usage of GeoDataFrames used in the solver through generating dummy data and running the solver guarenteeing that the GeoDataFrames are handled correctly

The tests ensure that the `solve_capacitated_flp` function consistently returns the expected data types and structures (list of opened facilities, dictionary of assignments, and solving time).

import json
import os
import sys
import unittest
from unittest.mock import patch

import numpy as np
from facility_location.helper.solver_util import (
    create_dummy_pharmacy_data,
    create_dummy_prac_data,
)

# Add the path to the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import the CFLP solver function
# Assuming solve_capacitated_flp is now in helper/solver_util.py
from facility_location.solver import solve_capacitated_flp


# Custom JSON encoder for NumPy types (keep this)
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class TestCapacitatedFLP(unittest.TestCase):
    # Testcase 1: Basic CFLP with known capacities
    def test_basic_cflp_solution(self):
        cost_matrix = {
            "PRAC1": {"F_A": 10, "F_B": 20},
            "PRAC2": {"F_A": 5, "F_B": 12},
        }
        # Define demands for each practitioner in this test case
        demand_quantities = {
            "PRAC1": 1,  # Assuming each practitioner has a demand of 1 unit
            "PRAC2": 1,
        }
        capacities = {"F_A": 2, "F_B": 1}  # These are facility_capacities
        open_cost = 1.0  # This is fixcost

        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,  # Pass capacities here
                demand_quantities=demand_quantities,  # Pass demands here
                fixcost=open_cost,  # Pass open_cost here
            )

        self.assertIsInstance(open_facilities, list)
        self.assertEqual(len(open_facilities), 1)
        self.assertIn("F_A", open_facilities)

        self.assertIsInstance(assignments, dict)
        self.assertEqual(assignments.get("PRAC1"), "F_A")
        self.assertEqual(assignments.get("PRAC2"), "F_A")

    # Testcase 2: Capacity limit blocks assignment
    def test_capacity_blocking(self):
        cost_matrix = {
            "PRAC1": {"F_A": 1, "F_B": 10},  # Added F_B
            "PRAC2": {"F_A": 2, "F_B": 8},  # Added F_B
            "PRAC3": {"F_A": 3, "F_B": 5},  # Added F_B
        }
        # Define demands for each practitioner
        demand_quantities = {
            "PRAC1": 1,
            "PRAC2": 1,
            "PRAC3": 1,
        }
        capacities = {"F_A": 2, "F_B": 1}  # facility_capacities
        open_cost = 0.5  # fixcost

        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,
                demand_quantities=demand_quantities,
                fixcost=open_cost,
            )

        self.assertIn("F_B", open_facilities)  # F_B must be opened to serve PRAC3
        self.assertEqual(len(assignments), 3)  # All demands should be met
        self.assertEqual(assignments.get("PRAC1"), "F_A")
        self.assertEqual(assignments.get("PRAC2"), "F_A")
        self.assertEqual(assignments.get("PRAC3"), "F_B")

    # Testcase 3: Empty cost matrix
    def test_empty_cost_matrix(self):
        cost_matrix = {}
        capacities = {}
        demand_quantities = {}  # Must pass empty demand quantities
        open_cost = 1.0

        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,
                demand_quantities=demand_quantities,
                fixcost=open_cost,
            )

        self.assertEqual(open_facilities, [])
        self.assertEqual(assignments, {})
        self.assertAlmostEqual(solving_time, 0.0)

    # Testcase 4: Facility with zero capacity
    def test_zero_capacity(self):
        cost_matrix = {
            "PRAC1": {"F_A": 10, "F_B": 1},
        }
        demand_quantities = {
            "PRAC1": 1,
        }
        capacities = {"F_A": 0, "F_B": 1}
        open_cost = 0.1

        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,
                demand_quantities=demand_quantities,
                fixcost=open_cost,
            )

        self.assertIn("F_B", open_facilities)
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments.get("PRAC1"), "F_B")
        self.assertNotIn("PRAC2", assignments)

    # Testcase 5: High open cost with capacity
    def test_high_open_cost_with_capacity(self):
        cost_matrix = {
            "PRAC1": {"F_A": 1, "F_B": 100},
            "PRAC2": {"F_A": 100, "F_B": 1},
        }
        demand_quantities = {
            "PRAC1": 1,
            "PRAC2": 1,
        }
        capacities = {"F_A": 1, "F_B": 1}  # Each facility can serve 1 unit
        open_cost = 10.0  # This is a relatively high open cost

        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,
                demand_quantities=demand_quantities,
                fixcost=open_cost,
            )

        # With high open_cost, the solver might try to open fewer facilities if possible.
        # The assignment should follow the highest cost paths.
        self.assertEqual(set(open_facilities), {"F_A", "F_B"})
        self.assertEqual(assignments.get("PRAC1"), "F_A")
        self.assertEqual(assignments.get("PRAC2"), "F_B")

        # Testcase 6: Using dummy GeoDataFrame functions

    def test_with_dummy_geodataframes(self):
        # Generate dummy GeoDataFrames using the dedicated functions
        practitioners_gdf = create_dummy_prac_data()
        pharmacies_gdf = create_dummy_pharmacy_data()

        # Process GDFs into solver inputs (replicating logic from solver.py)
        practitioners_gdf["string_id"] = practitioners_gdf.index.astype(str)
        pharmacies_gdf["string_id"] = pharmacies_gdf.index.astype(str)

        demand_quantities = {gp_id: 1 for gp_id in practitioners_gdf["string_id"]}
        capacities = {ph_id: 5 for ph_id in pharmacies_gdf["string_id"]}
        # For this test, we create a uniform cost matrix.
        cost_matrix = {
            prac_id: {ph_id: 10 for ph_id in pharmacies_gdf["string_id"]}
            for prac_id in practitioners_gdf["string_id"]
        }
        open_cost = 1.0

        # Run the solver with the data derived from dummy GDFs
        with patch("builtins.print"):
            open_facilities, assignments, solving_time = solve_capacitated_flp(
                cost_matrix=cost_matrix,
                facility_capacities=capacities,
                demand_quantities=demand_quantities,
                fixcost=open_cost,
            )

        # Assert basic results based on the generated data
        # With 10 practitioners and a capacity of 5 per facility, 2 facilities must open.
        self.assertIsInstance(open_facilities, list)
        self.assertEqual(len(open_facilities), 2)
        self.assertIsInstance(assignments, dict)
        self.assertEqual(len(assignments), len(practitioners_gdf))

        # Verify that all assignments are made to facilities that are actually open
        for prac_id, fac_id in assignments.items():
            self.assertIn(fac_id, open_facilities)


if __name__ == "__main__":
    unittest.main()

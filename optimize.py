import sqlite3
import pandas as pd
from ortools.linear_solver import pywraplp
from datetime import datetime

DB = "energy.db"


def fetch_data(conn):
    """Fetches all necessary data from the database in one go."""
    forecast_q = "SELECT timestamp, machine_id, predicted_demand FROM forecasts ORDER BY machine_id, timestamp"
    forecast_df = pd.read_sql_query(forecast_q, conn, parse_dates=["timestamp"])

    specs_q = """
        SELECT machine_id, AVG(energy_per_unit) as energy_per_unit, AVG(max_capacity) as max_capacity
        FROM raw_data
        WHERE timestamp > (SELECT MAX(timestamp) FROM raw_data) - '1 day'
        GROUP BY machine_id
    """
    specs_df = pd.read_sql_query(specs_q, conn).set_index('machine_id')

    cost_q = "SELECT machine_id, hour, AVG(energy_cost) as energy_cost FROM raw_data GROUP BY machine_id, hour"
    cost_df = pd.read_sql_query(cost_q, conn)

    # Create a lookup dictionary for fast access: (machine_id, hour) -> cost
    energy_cost_map = cost_df.set_index(['machine_id', 'hour'])['energy_cost'].to_dict()

    return forecast_df, specs_df, energy_cost_map


def optimize_all(conn):
    """Runs the full optimization process to minimize energy costs."""
    forecast_df, specs_df, energy_cost_map = fetch_data(conn)

    if forecast_df.empty:
        print("No forecasts found. Run forecast.py first.")
        return

    timestamps = sorted(forecast_df['timestamp'].unique())
    machines = sorted(forecast_df['machine_id'].unique())
    default_cost = 0.15  # A fallback energy cost

    # 1. Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("SCIP solver not available.")
        return

    # 2. Define production variables
    # production[(m, t)] is the amount machine 'm' produces at timestamp 't'
    production = {}
    for mid in machines:
        for ts in timestamps:
            max_cap = specs_df.loc[mid, 'max_capacity']
            production[(mid, ts)] = solver.NumVar(0, max_cap, f"prod_{mid}_{ts}")

    # 3. Define Constraints
    # Constraint 1: Total plant production at any hour cannot exceed an overall limit
    plant_capacity_limit = specs_df['max_capacity'].sum() * 0.9
    for ts in timestamps:
        solver.Add(sum(production[(m, ts)] for m in machines) <= plant_capacity_limit)

    # Constraint 2: A machine cannot produce more than its predicted demand for that hour
    pred_map = {(r['machine_id'], r['timestamp']): r['predicted_demand'] for _, r in forecast_df.iterrows()}
    for mid in machines:
        for ts in timestamps:
            solver.Add(production[(mid, ts)] <= pred_map.get((mid, ts), 0))

    # 4. Define the Objective Function (minimize total cost)
    objective = solver.Objective()
    for mid in machines:
        for ts in timestamps:
            energy_per_unit = specs_df.loc[mid, 'energy_per_unit']
            energy_cost = energy_cost_map.get((mid, ts.hour), default_cost)
            cost_coefficient = energy_per_unit * energy_cost
            objective.SetCoefficient(production[(mid, ts)], cost_coefficient)
    objective.SetMinimization()

    # 5. Solve the model
    print("Solving optimization problem...")
    status = solver.Solve()

    # 6. Process and Persist Results
    if status == pywraplp.Solver.OPTIMAL:
        print(f"Optimal solution found! Total minimized cost: {objective.Value():.2f}")
        cur = conn.cursor()
        cur.execute("DELETE FROM optimizations")  # Clear old results

        results = []
        for mid in machines:
            for ts in timestamps:
                opt_prod = production[(mid, ts)].solution_value()

                # Calculate baseline for comparison
                baseline_prod = min(pred_map.get((mid, ts), 0), specs_df.loc[mid, 'max_capacity'])

                # Get costs for calculation
                energy_per_unit = specs_df.loc[mid, 'energy_per_unit']
                energy_cost = energy_cost_map.get((mid, ts.hour), default_cost)

                opt_cost = opt_prod * energy_per_unit * energy_cost
                base_cost = baseline_prod * energy_per_unit * energy_cost

                results.append((
                    ts.strftime("%Y-%m-%d %H:%M:%S"), mid, ts.hour,
                    float(opt_prod), int(baseline_prod), float(opt_cost), float(base_cost)
                ))

        cur.executemany("""
            INSERT INTO optimizations (timestamp, machine_id, hour, optimized_production, baseline_production, optimized_cost, baseline_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, results)
        conn.commit()
        print(" Optimization complete and results have been saved to the database.")
    else:
        print("The problem does not have an optimal solution.")


def main():
    conn = sqlite3.connect(DB)
    optimize_all(conn)
    conn.close()



if __name__ == "__main__":
    main()
import sqlite3
import pandas as pd

DB = "energy.db"
CSV = "energy_data.csv"


def create_tables(conn):
    """Creates all necessary tables with the correct schema."""
    cur = conn.cursor()
    # Table for raw time-series data
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            hour INTEGER,
            machine_id TEXT NOT NULL,
            energy_per_unit REAL,
            production_demand INTEGER,
            max_capacity INTEGER,
            energy_cost REAL
        )
        """
    )
    # Table for storing model forecasts
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            machine_id TEXT NOT NULL,
            predicted_demand REAL
        )
        """
    )
    # Table for storing optimization results
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            machine_id TEXT NOT NULL,
            hour INTEGER,
            optimized_production REAL,
            baseline_production INTEGER,
            optimized_cost REAL,
            baseline_cost REAL
        )
        """
    )
    conn.commit()


def load_csv(conn, csv_path):
    """Loads CSV data into the 'raw_data' table, preserving the original schema."""
    try:
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])

        # --- FIX: Preserve the table schema created by CREATE TABLE ---
        # Clear the table first to prevent duplicating data on re-runs
        cur = conn.cursor()
        cur.execute("DELETE FROM raw_data")
        conn.commit()

        # Use if_exists="append" to load data into the existing table structure
        df.to_sql("raw_data", conn, if_exists="append", index=False)
        print(f"Loaded {len(df)} rows into 'raw_data' table.")

    except FileNotFoundError:
        print(f"Error: The file {csv_path} was not found. Please ensure it is in the correct directory.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """Initializes the database, creates tables, and loads initial data."""
    conn = sqlite3.connect(DB)
    create_tables(conn)
    load_csv(conn, CSV)
    conn.close()
    print(f"Database setup complete. DB: {DB}")



if __name__ == "__main__":
    main()
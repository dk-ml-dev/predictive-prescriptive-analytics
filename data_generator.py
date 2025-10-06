import csv
import random
import math
import pandas as pd
from datetime import datetime, timedelta

NUM_MACHINES = 10
HOURS = 24 * 14  # two weeks of hourly history for better forecasting
MACHINE_IDS = [f"M{idx + 1}" for idx in range(NUM_MACHINES)]
START = datetime.now() - timedelta(hours=HOURS)


def generate_machine_profile(mid):
    """Creates a random performance profile for a single machine."""
    base = round(random.uniform(1.5, 4.0), 2)  # baseline energy per unit (kWh)
    cap = random.randint(40, 120)  # machine capacity (units per hour)
    return {"machine_id": mid, "energy_per_unit": base, "max_capacity": cap}


def energy_cost_hour(hour_index):
    """Calculates energy cost based on the time of day."""
    hour_of_day = (START + timedelta(hours=hour_index)).hour
    # Peak hours (9 AM to 9 PM) have higher costs
    if 9 <= hour_of_day <= 21:
        return round(0.18 + 0.02 * math.sin(hour_of_day / 3), 3)  # Peak: ~0.18-0.21 $/kWh
    # Off-peak hours
    else:
        return round(0.10 + 0.01 * math.sin(hour_of_day / 4), 3)  # Off-peak: ~0.09-0.12 $/kWh


def generate_time_series():
    """Generates the full time-series dataset for all machines."""
    rows = []
    profiles = {mid: generate_machine_profile(mid) for mid in MACHINE_IDS}

    for h in range(HOURS):
        timestamp = START + timedelta(hours=h)
        for mid in MACHINE_IDS:
            profile = profiles[mid]
            hour_of_day = timestamp.hour

            # Base demand varies with a daily cycle and randomness
            daily_factor = 1.0 + 0.6 * math.sin((hour_of_day / 24.0) * 2 * math.pi)
            base_demand = int(profile["max_capacity"] * (0.4 + 0.6 * random.random()) * daily_factor)

            # Occasionally spike demand to simulate higher production days
            if random.random() < 0.02:
                base_demand = min(profile["max_capacity"], base_demand + random.randint(10, 50))

            # --- FIX: The following lines were moved out of the 'if' block ---
            # This ensures a row is created for EVERY hour, not just during a spike.
            energy_cost = energy_cost_hour(h)
            rows.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "hour": timestamp.hour,
                "machine_id": mid,
                "energy_per_unit": profile["energy_per_unit"],
                "production_demand": base_demand,
                "max_capacity": profile["max_capacity"],
                "energy_cost": energy_cost
            })

    return pd.DataFrame(rows)


def main():
    """Main function to generate and save the data."""
    df = generate_time_series()
    df.to_csv("energy_data.csv", index=False)
    print("Generated energy_data.csv with", len(df), "rows.")



if __name__ == "__main__":
    main()
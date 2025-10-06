import sqlite3
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

DB = "energy.db"

# Check for optional libraries and set flags
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA

    SM_AVAILABLE = True
except ImportError:
    SM_AVAILABLE = False


def load_data(conn):
    """Loads and preprocesses data from the SQLite database."""
    df = pd.read_sql_query("SELECT * FROM raw_data", conn, parse_dates=["timestamp"])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def make_sequences(series, window=24):
    """Creates sequences for LSTM model training."""
    X, y = [], []
    for i in range(len(series) - window):
        X.append(series[i:i + window])
        y.append(series[i + window])
    return np.array(X), np.array(y)


def lstm_forecast(series, steps=24, epochs=8):
    """Generates a forecast using an LSTM model."""
    series = series.astype(np.float32)
    X, y = make_sequences(series, window=24)
    if len(X) < 10:
        raise ValueError("Not enough data to train LSTM model.")

    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(32, input_shape=(X.shape[1], 1)),
        Dense(16, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=epochs, verbose=0)

    last_window = series[-24:].reshape((1, 24, 1))
    preds = []
    cur_window = last_window
    for _ in range(steps):
        p = model.predict(cur_window, verbose=0)[0, 0]
        preds.append(float(p))
        # Slide the window forward with the new prediction
        arr = np.append(cur_window.flatten()[1:], p)
        cur_window = arr.reshape((1, 24, 1))
    return preds


def arima_forecast(series, steps=24):
    """Generates a forecast using an ARIMA model."""
    if len(series) < 30:
        raise ValueError("Not enough data for ARIMA model.")
    # A common and robust order for general time series
    model = ARIMA(series, order=(5, 1, 0))
    res = model.fit()
    f = res.forecast(steps=steps)
    return [float(x) for x in f]


def persist_forecasts(conn, machine_id, base_time, preds):
    """Deletes old forecasts and inserts new ones into the database."""
    cur = conn.cursor()

    # --- FIX: Delete old forecasts for the same time period before inserting new ones ---
    start_ts = (base_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_ts = (base_time + timedelta(hours=len(preds))).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "DELETE FROM forecasts WHERE machine_id = ? AND timestamp BETWEEN ? AND ?",
        (machine_id, start_ts, end_ts)
    )

    forecast_data = []
    for i, val in enumerate(preds):
        ts = (base_time + timedelta(hours=i + 1)).strftime("%Y-%m-%d %H:%M:%S")
        forecast_data.append((ts, machine_id, float(val)))

    cur.executemany(
        "INSERT INTO forecasts (timestamp, machine_id, predicted_demand) VALUES (?, ?, ?)",
        forecast_data
    )
    conn.commit()


def main():
    """Main function to run the forecasting pipeline."""
    conn = sqlite3.connect(DB)
    df = load_data(conn)

    if df.empty:
        print("No data found in raw_data table.")
        conn.close()
        return

    now = df['timestamp'].max()
    machines = df['machine_id'].unique()

    for m in machines:
        series = df[df['machine_id'] == m].sort_values('timestamp')['production_demand'].reset_index(drop=True)


        try:
            if TF_AVAILABLE:
                print(f"Attempting LSTM forecast for machine {m}...")
                preds = lstm_forecast(series.values, steps=24, epochs=10)
            elif SM_AVAILABLE:
                print(f"Attempting ARIMA forecast for machine {m}...")
                preds = arima_forecast(series, steps=24)
            else:
                print(f"No forecasting libraries available. Using naive forecast for machine {m}.")
                preds = [float(series.iloc[-1])] * 24
        except Exception as e:
            print(f"Forecast error for {m}: {e} — falling back to naive forecast.")
            preds = [float(series.iloc[-1])] * 24  # Fallback logic is now inside the except block

        persist_forecasts(conn, m, now, preds)
        print(f"Persisted forecast for machine {m} (24 steps)")

    conn.close()
    print("\nForecasting complete.")



if __name__ == "__main__":
    main()
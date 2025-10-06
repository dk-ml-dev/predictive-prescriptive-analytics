# ⚡ Energy Optimization in Manufacturing (Industry 4.0)

## 📖 Overview

This project demonstrates how **Machine Learning (ML)** and **Operations Research (OR)** can be integrated to enable **smart manufacturing and Industry 4.0** solutions. It simulates real-world factory data, predicts energy demand, and optimizes machine schedules to minimize energy costs — achieving efficiency, sustainability, and cost savings.

---

## 🧠 Problem Statement

Manufacturing plants operate multiple machines that consume varying amounts of energy depending on production demand. Energy costs fluctuate throughout the day (peak vs off-peak). Without optimization, plants face inefficiencies and high operational costs.

**Goal:**

* Predict future energy demand using ML models.
* Optimize machine operations to minimize total energy cost.
* Visualize insights in a real-time dashboard.

---

## 🚀 Key Features

* 🏭 **Synthetic Data Generator:** Simulates hourly production and energy consumption data for multiple machines.
* 📊 **Forecasting (Predictive Analytics):** Uses **LSTM** (or **ARIMA** fallback) to predict next 24-hour energy demand.
* ⚙️ **Optimization (Prescriptive Analytics):** Uses **OR-Tools Linear Programming** to allocate production under cost and capacity constraints.
* 💾 **Database Integration:** Stores data, forecasts, and optimization results in **SQLite** (ready for Power BI or Tableau).
* 📈 **Interactive Dashboard:** Built with **Streamlit** + **Altair**, visualizing cost savings, forecasts, and optimized schedules.

---

## 🧰 Tech Stack

| Category             | Tools / Libraries                                    |
| -------------------- | ---------------------------------------------------- |
| **Programming**      | Python 3.x                                           |
| **Data Science**     | Pandas, NumPy, Scikit-learn, Statsmodels, TensorFlow |
| **Optimization**     | Google OR-Tools                                      |
| **Database**         | SQLite, SQLAlchemy                                   |
| **Visualization**    | Streamlit, Altair, Matplotlib                        |
| **Deployment Ready** | Azure ML, Power BI integration supported             |

---

## 🗂 Project Structure

```
energy_optimization/
├── data_generator.py      # Generate synthetic data
├── db_setup.py            # Create and populate SQLite database
├── forecast.py            # Predict energy demand (LSTM/ARIMA)
├── optimize.py            # Run optimization model (OR-Tools)
├── app_streamlit.py       # Dashboard app for visualization
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Setup & Execution

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/energy-optimization-manufacturing.git
cd energy-optimization-manufacturing
```

### 2️⃣ Install Dependencies

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3️⃣ Generate Data and Initialize Database

```bash
python data_generator.py
python db_setup.py
```

### 4️⃣ Train Forecasting Model

```bash
python forecast.py
```

### 5️⃣ Run Optimization

```bash
python optimize.py
```

### 6️⃣ Launch Streamlit Dashboard

```bash
streamlit run app_streamlit.py
```

Then open your browser at: **[http://localhost:8501](http://localhost:8501)**

---

## 🚀 Live Demo

Check out the live, interactive dashboard here:

👉 **[View Energy Optimization Dashboard](https://predictive-prescriptive-analytics-4djxxxtil5mmhbqbplwp3q.streamlit.app/)**

This Streamlit app lets you:

* Forecast energy demand for each machine using ML models (LSTM / ARIMA).
* Optimize production schedules using OR-Tools Linear Programming.
* Compare **baseline vs optimized energy cost** with visual charts.
* View machine-level performance, savings, and key metrics in real time.

---

## 📈 Results

* Forecasted next 24-hour machine energy demand using LSTM.
* Optimized production schedule with **~20% simulated cost savings**.
* Created dashboards showing real-time cost comparisons and machine-level efficiency.

---

## 🏢 Business Value

This project reflects how **Data Science + Optimization** can transform traditional manufacturing into a **smart, connected, sustainable operation**.
It demonstrates skills that align with roles at organizations like **P&G**, focusing on:

* Process optimization
* Cost reduction
* Predictive & prescriptive analytics
* Digital transformation in manufacturing

---

## 🔖 Tags / Topics

`machine-learning` `optimization` `or-tools` `smart-manufacturing`
`energy-efficiency` `predictive-analytics` `prescriptive-analytics`
`industry-4.0` `python` `streamlit` `sqlite`

---

## 🧩 Future Improvements

* Integrate with **Azure Data Factory / Databricks** pipelines.
* Add live IoT data ingestion from sensors.
* Deploy as an **Azure ML endpoint** for cloud inference.
* Build Power BI dashboard on top of SQLite data.

---

## 👨‍💻 Author

**Deepu Kushwaha**
📧 [deepu05.kushwaha@gmail.com](mailto:deepu05.kushwaha@gmail.com)
🔗 [LinkedIn](https://linkedin.com/in/deepukushwaha) | [GitHub](https://github.com/dk-ml-dev)

---

⭐ *If you like this project, give it a star on GitHub to support future AI + optimization projects!* ⭐

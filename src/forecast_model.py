import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Load environment variables
load_dotenv()


# Create MySQL connection
db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(db_url)


# Load sales data from MySQL
query = """
SELECT
    order_date,
    sales
FROM sales
ORDER BY order_date;
"""

df = pd.read_sql(query, engine)


print("Data loaded successfully!")
print("Rows:", len(df))
print(df.head())
# Convert order_date to datetime
df["order_date"] = pd.to_datetime(df["order_date"])

# Create monthly sales
monthly_sales = (
    df.set_index("order_date")
      .resample("MS")["sales"]
      .sum()
      .reset_index()
)

print("\nMonthly sales:")
print(monthly_sales.head())

print("\nMonthly sales shape:", monthly_sales.shape)
# Create time-based features
monthly_sales["year"] = monthly_sales["order_date"].dt.year
monthly_sales["month"] = monthly_sales["order_date"].dt.month
monthly_sales["quarter"] = monthly_sales["order_date"].dt.quarter

# Create lag features
monthly_sales["lag_1"] = monthly_sales["sales"].shift(1)
monthly_sales["lag_2"] = monthly_sales["sales"].shift(2)
monthly_sales["lag_3"] = monthly_sales["sales"].shift(3)

# Create rolling average features
monthly_sales["rolling_3"] = (
    monthly_sales["sales"]
    .shift(1)
    .rolling(window=3)
    .mean()
)

# Remove rows created by lag/rolling calculations
monthly_sales = monthly_sales.dropna().reset_index(drop=True)

print("\nFeatures created:")
print(monthly_sales.head())

print("\nFinal dataset shape:", monthly_sales.shape)
# Define features and target
features = [
    "year",
    "month",
    "quarter",
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_3"
]

X = monthly_sales[features]
y = monthly_sales["sales"]

# Time-based train-test split
split_index = int(len(monthly_sales) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining period:")
print(monthly_sales["order_date"].iloc[0], "to",
      monthly_sales["order_date"].iloc[split_index - 1])

print("\nTesting period:")
print(monthly_sales["order_date"].iloc[split_index], "to",
      monthly_sales["order_date"].iloc[-1])
from xgboost import XGBRegressor

# Create XGBoost model
model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective="reg:squarederror"
)

# Train the model
model.fit(X_train, y_train)

print("\nXGBoost model trained successfully!")
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Make predictions on test data
y_pred = model.predict(X_test)

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation")
print("----------------")
print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("R²  :", round(r2, 4))
import joblib
import os

# Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# Save trained model
model_path = "models/sales_forecasting_model.pkl"
joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Saved to:", model_path)
# Generate future 3-month forecast

history = monthly_sales[["order_date", "sales"]].copy()

future_predictions = []

for i in range(3):
    next_date = history["order_date"].iloc[-1] + pd.DateOffset(months=1)

    year = next_date.year
    month = next_date.month
    quarter = next_date.quarter

    lag_1 = history["sales"].iloc[-1]
    lag_2 = history["sales"].iloc[-2]
    lag_3 = history["sales"].iloc[-3]

    rolling_3 = history["sales"].iloc[-3:].mean()

    future_features = pd.DataFrame({
        "year": [year],
        "month": [month],
        "quarter": [quarter],
        "lag_1": [lag_1],
        "lag_2": [lag_2],
        "lag_3": [lag_3],
        "rolling_3": [rolling_3]
    })

    prediction = model.predict(future_features)[0]

    future_predictions.append({
        "order_date": next_date,
        "predicted_sales": prediction
    })

    # Add prediction to history so the next month can use it
    history = pd.concat(
        [
            history,
            pd.DataFrame({
                "order_date": [next_date],
                "sales": [prediction]
            })
        ],
        ignore_index=True
    )

forecast_df = pd.DataFrame(future_predictions)

print("\nFuture Sales Forecast")
print("---------------------")
print(forecast_df)
import matplotlib.pyplot as plt

# Plot historical sales
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales["order_date"],
    monthly_sales["sales"],
    label="Historical Sales"
)

# Plot forecast
plt.plot(
    forecast_df["order_date"],
    forecast_df["predicted_sales"],
    marker="o",
    linestyle="--",
    label="Forecast"
)

plt.title("Monthly Sales Forecast")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save chart
os.makedirs("screenshots", exist_ok=True)

chart_path = "screenshots/sales_forecast.png"
plt.savefig(chart_path, dpi=300)

plt.show()

print("\nForecast chart saved to:", chart_path)

# Save forecast results
forecast_path = "data/processed/sales_forecast.csv"

forecast_df.to_csv(
    forecast_path,
    index=False
)

print("\nForecast saved successfully!")
print("Saved to:", forecast_path)
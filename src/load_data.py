import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Load environment variables
load_dotenv()

# MySQL connection
db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(db_url)

# Load cleaned dataset
file_path = "data/processed/superstore_clean.csv"

df = pd.read_csv(
    file_path,
    parse_dates=["Order Date", "Ship Date"]
)

# Rename columns to match MySQL table
df.columns = [
    "row_id",
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_id",
    "customer_name",
    "segment",
    "country",
    "city",
    "state",
    "postal_code",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit"
]

# Convert dates
df["order_date"] = df["order_date"].dt.date
df["ship_date"] = df["ship_date"].dt.date

# Load data into MySQL
df.to_sql(
    "sales",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=500
)

# Verify row count
with engine.connect() as connection:
    result = connection.execute(
        text("SELECT COUNT(*) FROM sales")
    )
    count = result.scalar()

print("Data loaded successfully!")
print("Rows in MySQL:", count)

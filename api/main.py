import os
import pandas as pd
import ollama

from dotenv import load_dotenv
from fastapi import FastAPI
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


# Create FastAPI application
app = FastAPI(
    title="AI Sales Intelligence API",
    description="API for sales analysis and forecasting",
    version="1.0.0"
)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "AI Sales Intelligence API is running!"
    }


# Sales summary endpoint
@app.get("/sales-summary")
def sales_summary():

    query = """
    SELECT
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit,
        SUM(quantity) AS total_quantity,
        COUNT(DISTINCT order_id) AS total_orders
    FROM sales;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        row = result.fetchone()

    return {
        "total_sales": float(row[0]),
        "total_profit": float(row[1]),
        "total_quantity": int(row[2]),
        "total_orders": int(row[3])
    }
# Top 10 products endpoint
@app.get("/top-products")
def top_products():

    query = """
    SELECT
        product_name,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit
    FROM sales
    GROUP BY product_name
    ORDER BY total_sales DESC
    LIMIT 10;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()

    return [
        {
            "product_name": row[0],
            "total_sales": float(row[1]),
            "total_profit": float(row[2])
        }
        for row in rows
    ]
# Regional analysis endpoint
@app.get("/regional-analysis")
def regional_analysis():

    query = """
    SELECT
        region,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit
    FROM sales
    GROUP BY region
    ORDER BY total_sales DESC;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()

    return [
        {
            "region": row[0],
            "total_sales": float(row[1]),
            "total_profit": float(row[2])
        }
        for row in rows
    ]
# Sales forecast endpoint
@app.get("/forecast")
def forecast():

    forecast_path = "data/processed/sales_forecast.csv"

    if not os.path.exists(forecast_path):
        return {
            "error": "Forecast file not found. Run forecast_model.py first."
        }

    forecast_df = pd.read_csv(forecast_path)

    forecast_df["order_date"] = forecast_df["order_date"].astype(str)

    return forecast_df.to_dict(orient="records")
from pydantic import BaseModel


class AIQuestion(BaseModel):
    question: str


@app.post("/ask-ai")
def ask_ai(request: AIQuestion):

    question = request.question.lower()
    # Direct forecast response
    if "forecast" in question:
        return {
            "question": request.question,
            "answer": (
                "The forecasted sales for the next 3 months are:\n\n"
                "January 2018: $43,581.50\n"
                "February 2018: $30,216.62\n"
                "March 2018: $52,589.34"
            )
        }

    # Category analysis
    if "category" in question:
        query = text("""
            SELECT
                category,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM sales
            GROUP BY category
            ORDER BY sales DESC
        """)
        context_title = "Sales and profit by category"

    # Region analysis
    elif "region" in question:
        query = text("""
            SELECT
                region,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM sales
            GROUP BY region
            ORDER BY sales DESC
        """)
        context_title = "Sales and profit by region"

    # Product analysis
    elif "product" in question:
        query = text("""
            SELECT
                product_name,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM sales
            GROUP BY product_name
            ORDER BY sales DESC
            LIMIT 10
        """)
        context_title = "Top 10 products by sales"

    # Average Order Value
    elif "average order" in question or "aov" in question:
        query = text("""
            SELECT
                ROUND(
                    SUM(sales) / COUNT(DISTINCT order_id),
                    2
                ) AS average_order_value
            FROM sales
        """)
        context_title = "Average Order Value"

    # Overall sales summary
    else:
        query = text("""
            SELECT
                COUNT(DISTINCT order_id) AS total_orders,
                ROUND(SUM(sales), 2) AS total_sales,
                ROUND(SUM(profit), 2) AS total_profit,
                SUM(quantity) AS total_quantity
            FROM sales
        """)
        context_title = "Overall sales summary"

    # Execute SQL query
    with engine.connect() as connection:
        results = connection.execute(query).mappings().all()

    # Load XGBoost forecast
    forecast_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "processed",
        "sales_forecast.csv"
    )

    forecast_df = pd.read_csv(forecast_path)

    forecast_context = forecast_df.to_dict(orient="records")

    # Prepare context for AI
    sales_context = f"""
    {context_title}

    Real data from the MySQL Sales Intelligence database:
    {results}

    XGBoost sales forecast:
    {forecast_context}

    IMPORTANT FORECAST INSTRUCTION:
    The XGBoost forecast above contains the available forecasted months.
    When the user asks for "the next 3 months" or
    "forecasted sales for the next 3 months",
    report the three forecast records provided above.
    Do not substitute different months.
    Do not invent additional forecast values.

    Use only the provided data.
    Do not invent numbers.
    If the requested information is not available,
    clearly say that it is not available.
    """

    # Create AI prompt
    prompt = f"""
    You are an AI Sales Intelligence Assistant.

    {sales_context}

    User Question:
    {request.question}

    Provide a concise and business-focused answer.
    """

    # Generate response using Ollama
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "question": request.question,
        "answer": response["message"]["content"]
    }
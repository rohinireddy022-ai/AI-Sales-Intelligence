import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "superstore_clean.csv"
)

st.set_page_config(
    page_title="AI Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PREMIUM UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f4f7fb;
}

.block-container {
    max-width: 1500px;
    padding: 1.4rem 2.5rem 3rem;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b1220 0%,
        #111c31 55%,
        #17243b 100%
    );
}

section[data-testid="stSidebar"] * {
    color: #f8fafc;
}

.sidebar-brand {
    font-size: 29px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
}

.sidebar-caption {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-bottom: 20px;
}

.sidebar-section {
    color: #cbd5e1 !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ================= HEADER ================= */

.hero-title {
    font-size: 43px;
    font-weight: 850;
    color: #0f172a;
    letter-spacing: -1.5px;
    margin-bottom: 0;
}

.hero-subtitle {
    color: #64748b;
    font-size: 16px;
    margin-top: 3px;
    margin-bottom: 18px;
}

.online-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 30px;
    background: #dcfce7;
    color: #166534;
    font-size: 12px;
    font-weight: 700;
}

/* ================= KPI ================= */

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 20px 21px;
    min-height: 125px;
    box-shadow: 0 5px 20px rgba(15,23,42,0.055);
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    transition: all 0.2s ease;
    box-shadow: 0 10px 28px rgba(15,23,42,0.10);
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
    font-size: 13px;
    font-weight: 650;
}

div[data-testid="stMetricValue"] {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
}

/* ================= SECTIONS ================= */

.section-title {
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
    margin-top: 30px;
    margin-bottom: 4px;
}

.section-description {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 16px;
}

/* ================= INSIGHT CARDS ================= */

.insight-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 100px;
    box-shadow: 0 4px 16px rgba(15,23,42,0.04);
}

.insight-title {
    color: #0f172a;
    font-size: 14px;
    font-weight: 750;
    margin-bottom: 6px;
}

.insight-text {
    color: #64748b;
    font-size: 13px;
    line-height: 1.5;
}

/* ================= AI ================= */

.ai-banner {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 55%,
        #263653 100%
    );
    border-radius: 22px;
    padding: 30px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(15,23,42,0.12);
}

.ai-banner h1,
.ai-banner h2 {
    color: white;
}

.ai-banner p {
    color: #cbd5e1;
}

/* ================= FORECAST ================= */

.forecast-banner {
    background: linear-gradient(
        135deg,
        #172554,
        #1e3a8a
    );
    border-radius: 20px;
    padding: 25px;
    color: white;
    margin-bottom: 20px;
}

.forecast-banner h2 {
    color: white;
}

.forecast-banner p {
    color: #dbeafe;
}

/* ================= TABLE ================= */

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ================= FOOTER ================= */

.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    padding: 25px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_csv(DATA_PATH)

    data["Order Date"] = pd.to_datetime(
        data["Order Date"]
    )

    data["Ship Date"] = pd.to_datetime(
        data["Ship Date"]
    )

    data["Year"] = data["Order Date"].dt.year

    data["Month"] = (
        data["Order Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return data


df = load_data()


# ============================================================
# API HELPERS
# ============================================================

def api_get(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:

        return None


def api_post(endpoint, payload):

    try:

        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:

        return None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">📊 AI Sales</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-caption">'
        'Intelligence Platform'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Executive Overview",
            "📊 Sales Analytics",
            "🔮 Forecast Center",
            "🤖 AI Sales Copilot"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">'
        'Technology Stack'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption("🐍 Python")
    st.caption("🐼 Pandas")
    st.caption("🗄️ MySQL")
    st.caption("⚡ XGBoost")
    st.caption("🚀 FastAPI")
    st.caption("🧠 Ollama + Llama 3.2")
    st.caption("📊 Streamlit")

    st.divider()

    st.caption(
        "End-to-end AI-powered sales "
        "analytics and forecasting."
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">'
    '📊 AI Sales Intelligence'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'Transform historical sales data into business insights, '
    'machine-learning forecasts and AI-powered answers.'
    '</div>',
    unsafe_allow_html=True
)

summary = api_get("/sales-summary")

if summary:

    st.markdown(
        '<span class="online-badge">'
        '● Backend Connected'
        '</span>',
        unsafe_allow_html=True
    )

else:

    st.error(
        "FastAPI backend is unavailable. "
        "Make sure Uvicorn is running."
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "🏠 Executive Overview":

    st.markdown(
        '<div class="section-title">'
        'Executive Overview'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Monitor overall business performance using '
        'interactive filters and visual analytics.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    f1, f2, f3, f4 = st.columns(4)

    with f1:

        year_options = [
            "All"
        ] + sorted(
            df["Year"].unique().tolist()
        )

        selected_year = st.selectbox(
            "📅 Year",
            year_options
        )

    with f2:

        category_options = [
            "All"
        ] + sorted(
            df["Category"].unique().tolist()
        )

        selected_category = st.selectbox(
            "🏷️ Category",
            category_options
        )

    with f3:

        region_options = [
            "All"
        ] + sorted(
            df["Region"].unique().tolist()
        )

        selected_region = st.selectbox(
            "🌎 Region",
            region_options
        )

    with f4:

        segment_options = [
            "All"
        ] + sorted(
            df["Segment"].unique().tolist()
        )

        selected_segment = st.selectbox(
            "👥 Segment",
            segment_options
        )

    filtered = df.copy()

    if selected_year != "All":

        filtered = filtered[
            filtered["Year"] == selected_year
        ]

    if selected_category != "All":

        filtered = filtered[
            filtered["Category"] == selected_category
        ]

    if selected_region != "All":

        filtered = filtered[
            filtered["Region"] == selected_region
        ]

    if selected_segment != "All":

        filtered = filtered[
            filtered["Segment"] == selected_segment
        ]

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_sales = filtered["Sales"].sum()

    total_profit = filtered["Profit"].sum()

    total_orders = filtered["Order ID"].nunique()

    total_quantity = filtered["Quantity"].sum()

    margin = (
        total_profit / total_sales * 100
        if total_sales else 0
    )

    st.markdown("")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric(
            "💰 Total Sales",
            f"${total_sales:,.0f}"
        )

    with k2:
        st.metric(
            "📈 Total Profit",
            f"${total_profit:,.0f}"
        )

    with k3:
        st.metric(
            "🛒 Orders",
            f"{total_orders:,}"
        )

    with k4:
        st.metric(
            "📦 Quantity",
            f"{total_quantity:,}"
        )

    with k5:
        st.metric(
            "💹 Profit Margin",
            f"{margin:.2f}%"
        )

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📈 Sales & Profit Trend'
        '</div>',
        unsafe_allow_html=True
    )

    monthly = (
        filtered
        .groupby("Month")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Sales"],
            mode="lines+markers",
            name="Sales"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Profit"],
            mode="lines+markers",
            name="Profit"
        )
    )

    fig.update_layout(
        title="Monthly Performance",
        xaxis_title="Month",
        yaxis_title="Amount",
        template="plotly_white",
        height=430,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CATEGORY + REGION
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    category_df = (
        filtered
        .groupby("Category")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    region_df = (
        filtered
        .groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    with c1:

        st.markdown(
            '<div class="section-title">'
            '🏷️ Category Performance'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.bar(
            category_df,
            x="Category",
            y="Sales",
            title="Sales by Category"
        )

        fig.update_layout(
            template="plotly_white",
            height=390
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        st.markdown(
            '<div class="section-title">'
            '🌎 Regional Performance'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.bar(
            region_df,
            x="Region",
            y="Sales",
            title="Sales by Region"
        )

        fig.update_layout(
            template="plotly_white",
            height=390
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # SEGMENT
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '👥 Customer Segments'
        '</div>',
        unsafe_allow_html=True
    )

    segment_df = (
        filtered
        .groupby("Segment")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    fig = px.bar(
        segment_df,
        x="Segment",
        y=["Sales", "Profit"],
        barmode="group",
        title="Sales and Profit by Customer Segment"
    )

    fig.update_layout(
        template="plotly_white",
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🏆 Top Products'
        '</div>',
        unsafe_allow_html=True
    )

    top_products = (
        filtered
        .groupby("Product Name")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .sort_values(
            "Sales",
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_products.sort_values("Sales"),
        x="Sales",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Sales"
    )

    fig.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # KEY INSIGHTS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '💡 Key Business Insights'
        '</div>',
        unsafe_allow_html=True
    )

    best_category = (
        category_df
        .sort_values("Sales", ascending=False)
        .iloc[0]
    )

    best_region = (
        region_df
        .sort_values("Sales", ascending=False)
        .iloc[0]
    )

    best_segment = (
        segment_df
        .sort_values("Sales", ascending=False)
        .iloc[0]
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">
                    🏷️ Leading Category
                </div>
                <div class="insight-text">
                    {best_category['Category']} generated
                    ${best_category['Sales']:,.2f}
                    in sales.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with i2:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">
                    🌎 Leading Region
                </div>
                <div class="insight-text">
                    {best_region['Region']} generated
                    ${best_region['Sales']:,.2f}
                    in sales.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with i3:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">
                    👥 Leading Segment
                </div>
                <div class="insight-text">
                    {best_segment['Segment']} generated
                    ${best_segment['Sales']:,.2f}
                    in sales.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SALES ANALYTICS
# ============================================================

elif page == "📊 Sales Analytics":

    st.markdown(
        '<div class="section-title">'
        '📊 Sales Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Detailed analysis of categories, regions, customers '
        'and profitability.'
        '</div>',
        unsafe_allow_html=True
    )

    # CATEGORY

    category_df = (
        df.groupby("Category")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    a1, a2 = st.columns(2)

    with a1:

        fig = px.bar(
            category_df,
            x="Category",
            y="Sales",
            title="Sales by Category"
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with a2:

        fig = px.bar(
            category_df,
            x="Category",
            y="Profit",
            title="Profit by Category"
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # REGION

    region_df = (
        df.groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    a1, a2 = st.columns(2)

    with a1:

        fig = px.bar(
            region_df,
            x="Region",
            y="Sales",
            title="Sales by Region"
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with a2:

        fig = px.bar(
            region_df,
            x="Region",
            y="Profit",
            title="Profit by Region"
        )

        fig.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # SEGMENTS

    segment_df = (
        df.groupby("Segment")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
        .reset_index()
    )

    fig = px.bar(
        segment_df,
        x="Segment",
        y=["Sales", "Profit"],
        barmode="group",
        title="Customer Segment Performance"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # PROFIT MARGIN

    margin_df = category_df.copy()

    margin_df["Profit Margin"] = (
        margin_df["Profit"]
        / margin_df["Sales"]
        * 100
    )

    fig = px.bar(
        margin_df,
        x="Category",
        y="Profit Margin",
        title="Profit Margin by Category",
        labels={
            "Profit Margin": "Profit Margin (%)"
        }
    )

    fig.update_layout(
        template="plotly_white",
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # TABLE

    st.markdown(
        '<div class="section-title">'
        '📋 Category Performance Details'
        '</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        margin_df.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FORECAST CENTER
# ============================================================

elif page == "🔮 Forecast Center":

    st.markdown(
        '<div class="forecast-banner">'
        '<h2>🔮 Forecast Center</h2>'
        '<p>'
        'Machine-learning based sales forecasting powered by XGBoost.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    forecast_data = api_get("/forecast")

    if forecast_data:

        forecast_df = pd.DataFrame(
            forecast_data
        )

        forecast_df["order_date"] = pd.to_datetime(
            forecast_df["order_date"]
        )

        # FORECAST CARDS

        fc1, fc2, fc3 = st.columns(3)

        for i, column in enumerate(
            [fc1, fc2, fc3]
        ):

            date = forecast_df.iloc[i][
                "order_date"
            ]

            value = forecast_df.iloc[i][
                "predicted_sales"
            ]

            with column:

                st.metric(
                    date.strftime("%B %Y"),
                    f"${value:,.2f}"
                )

        # CHART

        st.markdown(
            '<div class="section-title">'
            '📈 Predicted Sales Trend'
            '</div>',
            unsafe_allow_html=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=forecast_df["order_date"],
                y=forecast_df["predicted_sales"],
                mode="lines+markers",
                name="Predicted Sales"
            )
        )

        fig.update_layout(
            title="XGBoost 3-Month Sales Forecast",
            xaxis_title="Month",
            yaxis_title="Predicted Sales",
            template="plotly_white",
            height=460,
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # MODEL METRICS

        st.markdown(
            '<div class="section-title">'
            '🧠 Model Performance'
            '</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "MAE",
                "14,321.73"
            )

        with m2:
            st.metric(
                "RMSE",
                "17,793.00"
            )

        with m3:
            st.metric(
                "R² Score",
                "0.4917"
            )

        st.caption(
            "Model: XGBoost Regressor • "
            "Time-based 80/20 train-test split • "
            "Monthly sales forecasting"
        )

        # TABLE

        st.markdown(
            '<div class="section-title">'
            '📋 Forecast Details'
            '</div>',
            unsafe_allow_html=True
        )

        display_df = forecast_df.copy()

        display_df["order_date"] = display_df[
            "order_date"
        ].dt.strftime("%B %Y")

        display_df["predicted_sales"] = display_df[
            "predicted_sales"
        ].round(2)

        display_df.columns = [
            "Forecast Month",
            "Predicted Sales"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.error(
            "Unable to retrieve forecast data."
        )


# ============================================================
# AI SALES COPILOT
# ============================================================

elif page == "🤖 AI Sales Copilot":

    st.markdown(
        '<div class="ai-banner">'
        '<h2>🤖 AI Sales Copilot</h2>'
        '<p>'
        'Ask natural-language questions about your sales data, '
        'business performance and forecasts.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '💡 Suggested Questions'
        '</div>',
        unsafe_allow_html=True
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        st.info(
            "📊 Highest-sales category?"
        )

    with q2:
        st.info(
            "🌎 Highest-sales region?"
        )

    with q3:
        st.info(
            "🏆 Top products?"
        )

    with q4:
        st.info(
            "🔮 Next 3-month forecast?"
        )

    st.markdown("---")

    question = st.text_input(
        "Ask your business question",
        placeholder=(
            "Example: Which region has the highest sales?"
        )
    )

    ask = st.button(
        "🚀 Ask AI",
        type="primary"
    )

    if ask:

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "AI is analyzing your sales intelligence data..."
            ):

                result = api_post(
                    "/ask-ai",
                    {
                        "question": question
                    }
                )

            if result:

                st.markdown(
                    '<div class="section-title">'
                    '💬 AI Business Insight'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.success(
                    result.get(
                        "answer",
                        "No answer returned."
                    )
                )

                st.caption(
                    "Source: Sales Intelligence database + "
                    "XGBoost forecast context"
                )

            else:

                st.error(
                    "Unable to connect to the AI assistant."
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="footer">'
    'AI Sales Intelligence • '
    'Python • Pandas • MySQL • XGBoost • '
    'FastAPI • Ollama • Streamlit'
    '</div>',
    unsafe_allow_html=True
)
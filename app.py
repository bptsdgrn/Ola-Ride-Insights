import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
engine = create_engine(
    "postgresql+psycopg2://postgres:123@localhost:5432/Ola"
)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Ola Ride Analytics", layout="wide")

st.title("🚖 Ola Ride Analytics Dashboard")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filter Options")

vehicle_filter = st.sidebar.selectbox(
    "Select Vehicle Type",
    ["All"] + list(
        pd.read_sql("SELECT DISTINCT vehicle_type FROM ola_rides", engine)["vehicle_type"]
    )
)

status_filter = st.sidebar.selectbox(
    "Select Booking Status",
    ["All"] + list(
        pd.read_sql("SELECT DISTINCT booking_status FROM ola_rides", engine)["booking_status"]
    )
)

# -----------------------------
# BUILD WHERE CLAUSE
# -----------------------------
where_clause = "WHERE 1=1"

if vehicle_filter != "All":
    where_clause += f" AND vehicle_type = '{vehicle_filter}'"

if status_filter != "All":
    where_clause += f" AND booking_status = '{status_filter}'"

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3 = st.columns(3)

query_kpi = f"""
SELECT 
    COUNT(*) AS total_rides,
    SUM(booking_value) AS total_revenue,
    AVG(driver_ratings) AS avg_driver_rating
FROM ola_rides
{where_clause};
"""

kpi_df = pd.read_sql(query_kpi, engine)

col1.metric("Total Rides", int(kpi_df["total_rides"][0]))
col2.metric("Total Revenue", f"₹ {round(kpi_df['total_revenue'][0],2)}")
col3.metric("Avg Driver Rating", round(kpi_df["avg_driver_rating"][0],2))

# -----------------------------
# RIDE TREND
# -----------------------------
st.subheader("📈 Ride Trend Over Time")

query_trend = f"""
SELECT date,
       COUNT(*) AS rides
FROM ola_rides
{where_clause}
GROUP BY date
ORDER BY date;
"""

trend_df = pd.read_sql(query_trend, engine)
st.line_chart(trend_df.set_index("date"))

# -----------------------------
# REVENUE BY VEHICLE TYPE
# -----------------------------
st.subheader("💰 Revenue by Vehicle Type")

query_vehicle = f"""
SELECT vehicle_type,
       SUM(booking_value) AS revenue
FROM ola_rides
{where_clause}
GROUP BY vehicle_type
ORDER BY revenue DESC;
"""

vehicle_df = pd.read_sql(query_vehicle, engine)
st.bar_chart(vehicle_df.set_index("vehicle_type"))

# -----------------------------
# SEARCH CUSTOMER
# -----------------------------
st.subheader("🔎 Search by Customer ID")

customer_search = st.text_input("Enter Customer ID")

if customer_search:
    query_customer = f"""
    SELECT *
    FROM ola_rides
    WHERE customer_id = '{customer_search}';
    """
    customer_df = pd.read_sql(query_customer, engine)
    st.dataframe(customer_df)

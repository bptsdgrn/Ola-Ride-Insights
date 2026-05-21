import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine


engine = create_engine(
    "postgresql+psycopg2://postgres:123@localhost:5432/Ola"
)

st.set_page_config(page_title="Ola Ride Analytics", layout="wide")


st.markdown("""
<style>
    /* ---- Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    /* ---- Global ---- */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #0d0d0d;
        color: #f0f0f0;
    }

    /* ---- App background ---- */
    .stApp {
        background-color: #0d0d0d;
    }

    /* ---- Title ---- */
    h1 {
        color: #00e676 !important;
        font-weight: 700;
        letter-spacing: 1px;
        text-shadow: 0 0 18px #00e67655;
    }

    /* ---- Subheaders ---- */
    h2, h3 {
        color: #00e676 !important;
        font-weight: 600;
    }

    /* ---- Metric cards ---- */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a, #111);
        border: 1px solid #00e67633;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px #00e67620;
    }
    [data-testid="metric-container"] label {
        color: #aaaaaa !important;
        font-size: 0.85rem;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00e676 !important;
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #00e67622;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] header {
        color: #00e676 !important;
        font-weight: 600;
    }

    /* ---- Selectbox / Input ---- */
    .stSelectbox > div > div,
    .stTextInput > div > div {
        background-color: #1c1c1c !important;
        border: 1px solid #00e67655 !important;
        color: #f0f0f0 !important;
        border-radius: 8px;
    }

    /* ---- Divider ---- */
    hr {
        border-color: #00e67633;
    }

    /* ---- Dataframe ---- */
    .stDataFrame {
        border: 1px solid #00e67633;
        border-radius: 10px;
    }

    /* ---- Scrollbar ---- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #111; }
    ::-webkit-scrollbar-thumb { background: #00e676; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

OLA_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font=dict(color="#e0e0e0", family="Poppins"),
        colorway=["#00e676", "#69f0ae", "#00bfa5", "#1de9b6", "#76ff03", "#b9f6ca"],
        xaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a", zerolinecolor="#2a2a2a"),
        yaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a", zerolinecolor="#2a2a2a"),
    )
)


st.markdown("## 🚖 Ola Ride Analytics Dashboard")
st.markdown("---")


st.sidebar.markdown("### 🎛️ Filter Options")

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

where_clause = "WHERE 1=1"
if vehicle_filter != "All":
    where_clause += f" AND vehicle_type = '{vehicle_filter}'"
if status_filter != "All":
    where_clause += f" AND booking_status = '{status_filter}'"


query_kpi = f"""
SELECT
    COUNT(*) AS total_rides,
    SUM(booking_value) AS total_revenue,
    AVG(driver_ratings) AS avg_driver_rating
FROM ola_rides
{where_clause};
"""
kpi_df = pd.read_sql(query_kpi, engine)

col1, col2, col3 = st.columns(3)

total_rides   = kpi_df["total_rides"][0]
total_revenue = kpi_df["total_revenue"][0]
avg_rating    = kpi_df["avg_driver_rating"][0]

col1.metric("🚗 Total Rides", int(total_rides) if total_rides is not None else 0)
col2.metric("💰 Total Revenue", f"₹ {round(total_revenue, 2):,}" if total_revenue is not None else "₹ 0")
col3.metric("⭐ Avg Driver Rating", round(avg_rating, 2) if avg_rating is not None else "N/A")

st.markdown("---")


c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📈 Ride Trend Over Time")
    query_trend = f"""
    SELECT date, COUNT(*) AS rides
    FROM ola_rides
    {where_clause}
    GROUP BY date ORDER BY date;
    """
    trend_df = pd.read_sql(query_trend, engine)
    fig_line = px.line(
        trend_df, x="date", y="rides",
        markers=True,
        template=OLA_TEMPLATE,
        color_discrete_sequence=["#00e676"],
    )
    fig_line.update_traces(line_width=2.5, marker=dict(size=5, color="#00e676"))
    fig_line.update_layout(margin=dict(t=10, b=10), height=320)
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🥧 Booking Status")
    query_status = f"""
    SELECT booking_status, COUNT(*) AS count
    FROM ola_rides
    {where_clause}
    GROUP BY booking_status;
    """
    status_df = pd.read_sql(query_status, engine)
    fig_pie = px.pie(
        status_df, names="booking_status", values="count",
        template=OLA_TEMPLATE,
        color_discrete_sequence=["#00e676", "#69f0ae", "#00bfa5", "#1de9b6", "#b9f6ca"],
        hole=0.4,
    )
    fig_pie.update_traces(textfont_color="#ffffff", pull=[0.05] * len(status_df))
    fig_pie.update_layout(
        margin=dict(t=10, b=10), height=320,
        legend=dict(font=dict(color="#e0e0e0")),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")


c3, c4 = st.columns([3, 2])

with c3:
    st.subheader("💰 Revenue by Vehicle Type")
    query_vehicle = f"""
    SELECT vehicle_type, SUM(booking_value) AS revenue
    FROM ola_rides
    {where_clause}
    GROUP BY vehicle_type ORDER BY revenue DESC;
    """
    vehicle_df = pd.read_sql(query_vehicle, engine)
    fig_bar = px.bar(
        vehicle_df, x="vehicle_type", y="revenue",
        template=OLA_TEMPLATE,
        color="revenue",
        color_continuous_scale=["#003320", "#00e676"],
        text_auto=".2s",
    )
    fig_bar.update_traces(textfont_color="#ffffff", marker_line_width=0)
    fig_bar.update_layout(
        margin=dict(t=10, b=10), height=320,
        coloraxis_showscale=False,
        xaxis_title="Vehicle Type", yaxis_title="Revenue (₹)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("🍩 Rides per Vehicle Type")
    query_vtype = f"""
    SELECT vehicle_type, COUNT(*) AS rides
    FROM ola_rides
    {where_clause}
    GROUP BY vehicle_type;
    """
    vtype_df = pd.read_sql(query_vtype, engine)
    fig_donut = px.pie(
        vtype_df, names="vehicle_type", values="rides",
        template=OLA_TEMPLATE,
        color_discrete_sequence=["#00e676", "#69f0ae", "#00bfa5", "#1de9b6", "#76ff03"],
        hole=0.55,
    )
    fig_donut.update_traces(textfont_color="#ffffff")
    fig_donut.update_layout(
        margin=dict(t=10, b=10), height=320,
        legend=dict(font=dict(color="#e0e0e0")),
        annotations=[dict(
            text="Rides", x=0.5, y=0.5, font_size=16,
            font_color="#00e676", showarrow=False
        )]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")


c5, c6 = st.columns(2)

with c5:
    st.subheader("🔵 Distance vs Booking Value")
    query_scatter = f"""
    SELECT ride_distance, booking_value, vehicle_type
    FROM ola_rides
    {where_clause}
    LIMIT 500;
    """
    scatter_df = pd.read_sql(query_scatter, engine)
    fig_scatter = px.scatter(
        scatter_df, x="ride_distance", y="booking_value",
        color="vehicle_type",
        template=OLA_TEMPLATE,
        color_discrete_sequence=["#00e676", "#69f0ae", "#00bfa5", "#1de9b6", "#76ff03"],
        opacity=0.75,
    )
    fig_scatter.update_traces(marker=dict(size=6))
    fig_scatter.update_layout(
        margin=dict(t=10, b=10), height=320,
        xaxis_title="Distance (km)", yaxis_title="Booking Value (₹)",
        legend=dict(font=dict(color="#e0e0e0")),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with c6:
    st.subheader("⭐ Avg Rating by Vehicle Type")
    query_rating = f"""
    SELECT vehicle_type, ROUND(AVG(driver_ratings)::numeric, 2) AS avg_rating
    FROM ola_rides
    {where_clause}
    GROUP BY vehicle_type ORDER BY avg_rating DESC;
    """
    rating_df = pd.read_sql(query_rating, engine)
    fig_hbar = px.bar(
        rating_df, x="avg_rating", y="vehicle_type",
        orientation="h",
        template=OLA_TEMPLATE,
        color="avg_rating",
        color_continuous_scale=["#003320", "#00e676"],
        text_auto=".2f",
    )
    fig_hbar.update_traces(textfont_color="#ffffff", marker_line_width=0)
    fig_hbar.update_layout(
        margin=dict(t=10, b=10), height=320,
        coloraxis_showscale=False,
        xaxis_title="Avg Rating", yaxis_title="",
        xaxis=dict(range=[0, 5]),
    )
    st.plotly_chart(fig_hbar, use_container_width=True)

st.markdown("---")


st.subheader("🔎 Search by Customer ID")
customer_search = st.text_input("Enter Customer ID")
if customer_search:
    query_customer = f"""
    SELECT * FROM ola_rides
    WHERE customer_id = '{customer_search}';
    """
    customer_df = pd.read_sql(query_customer, engine)
    st.dataframe(customer_df, use_container_width=True)
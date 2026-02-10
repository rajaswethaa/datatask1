import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection

st.set_page_config(page_title="Churn Analysis", layout="wide")
st.title("⚠️ Customer Churn Analysis")

conn = get_connection()

# ---------------- LOAD CHURN DATA ----------------
@st.cache_data(ttl=600)
def load_churn():
    query = """
        SELECT *
        FROM VW_MONTHLY_CHURN
        ORDER BY MONTH_START
    """
    df = pd.read_sql(query, conn)
    df["MONTH_START"] = pd.to_datetime(df["MONTH_START"])
    return df

df = load_churn()

if df.empty:
    st.error("No churn data available in VW_MONTHLY_CHURN")
    st.stop()

# ---------------- DATE FILTER ----------------
min_date = df["MONTH_START"].min().date()
max_date = df["MONTH_START"].max().date()

date_range = st.slider(
    "Select Month Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)

filtered_df = df[
    (df["MONTH_START"].dt.date >= date_range[0]) &
    (df["MONTH_START"].dt.date <= date_range[1])
]

# ---------------- KPI CARDS ----------------
st.subheader("📌 Churn Summary")

total_customers = filtered_df["CUSTOMER_COUNT"].sum()
high_risk = filtered_df.loc[filtered_df["CHURN_RISK"] == "HIGH RISK", "CUSTOMER_COUNT"].sum()
medium_risk = filtered_df.loc[filtered_df["CHURN_RISK"] == "MEDIUM RISK", "CUSTOMER_COUNT"].sum()
low_risk = filtered_df.loc[filtered_df["CHURN_RISK"] == "LOW RISK", "CUSTOMER_COUNT"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{int(total_customers):,}")
c2.metric("High Risk", f"{int(high_risk):,}")
c3.metric("Medium Risk", f"{int(medium_risk):,}")
c4.metric("Low Risk", f"{int(low_risk):,}")

st.divider()

# ---------------- CHARTS ----------------
st.subheader("📊 Churn Distribution & Trend")

col1, col2 = st.columns(2)

# Pie chart → churn distribution
pie_fig = px.pie(
    filtered_df,
    names="CHURN_RISK",
    values="CUSTOMER_COUNT",
    title="Customer Churn Distribution"
)

# Line chart → churn trend over time
trend_fig = px.line(
    filtered_df,
    x="MONTH_START",
    y="CUSTOMER_COUNT",
    color="CHURN_RISK",
    markers=True,
    title="Monthly Churn Trend"
)

col1.plotly_chart(pie_fig, use_container_width=True)
col2.plotly_chart(trend_fig, use_container_width=True)

st.divider()

# ---------------- BAR CHART ----------------
st.subheader("📉 Churn Comparison by Month")

bar_fig = px.bar(
    filtered_df,
    x="MONTH_START",
    y="CUSTOMER_COUNT",
    color="CHURN_RISK",
    barmode="group",
    title="Monthly Churn Comparison"
)

st.plotly_chart(bar_fig, use_container_width=True)

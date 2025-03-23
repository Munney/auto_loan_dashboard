import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Auto Loan ABS Risk Dashboard", layout="wide")
st.title("Auto Loan ABS Risk Monitoring Dashboard")

def fetch_fred_data(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["observations"]
        df = pd.DataFrame(data)
        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        st.error("Failed to fetch data from FRED API")
        return pd.DataFrame()

api_key = st.secrets["FRED_API_KEY"]
subprime_delinquency_id = "DTSUBLPD"
manheim_index_id = "MANUVPI"

delinquency_df = fetch_fred_data(subprime_delinquency_id, api_key)
manheim_df = fetch_fred_data(manheim_index_id, api_key)

st.subheader("Subprime Auto Loan Delinquencies (60+ Days)")
if not delinquency_df.empty:
    fig = px.line(delinquency_df, x="date", y="value", title="Subprime Delinquencies Over Time")
    st.plotly_chart(fig)

st.subheader("Manheim Used Vehicle Value Index")
if not manheim_df.empty:
    fig2 = px.line(manheim_df, x="date", y="value", title="Used Vehicle Value Trends")
    st.plotly_chart(fig2)

st.sidebar.header("Alert Settings")
delinquency_threshold = st.sidebar.number_input("Delinquency Threshold (%)", min_value=0.0, value=7.0, step=0.1)
manheim_threshold = st.sidebar.number_input("Manheim Decline (%)", min_value=0.0, value=3.0, step=0.1)

latest_delinquency = delinquency_df.iloc[-1]["value"] if not delinquency_df.empty else 0
latest_manheim = (manheim_df.iloc[-1]["value"] - manheim_df.iloc[-2]["value"]) / manheim_df.iloc[-2]["value"] * 100 if not manheim_df.empty else 0

if latest_delinquency > delinquency_threshold:
    st.sidebar.warning(f"⚠️ Delinquencies have exceeded {delinquency_threshold}%! Current: {latest_delinquency}%")

if latest_manheim < -manheim_threshold:
    st.sidebar.warning(f"⚠️ Manheim Index declined more than {manheim_threshold}%. Current: {latest_manheim:.2f}%")

st.sidebar.info("Adjust alert thresholds to monitor critical signals.")
st.write("This dashboard tracks key auto loan ABS risk indicators and updates in real time.")

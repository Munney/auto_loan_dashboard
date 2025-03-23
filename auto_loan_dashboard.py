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
subprime_delinquency_id = "DRCLACBS"
manheim_index_id = "CUSR0000SETA02"

delinquency_df = fetch_fred_data(subprime_delinquency_id, api_key)
manheim_df = fetch_fred_data(manheim_index_id, api_key)

st.subheader("Subprime Auto Loan Delinquencies (60+ Days)")
if not delinquency_df.empty:
    fig = px.line(delinquency_df, x="date", y="value", title="Subprime Delinquencies Over Time")
    st.plotly_chart(fig)

st.subheader("Manheim Used Vehicle Value Index (Proxy: Used Car CPI)")
if not manheim_df.empty:
    fig2 = px.line(manheim_df, x="date", y="value", title="Used Vehicle Value Trends")
    st.plotly_chart(fig2)

st.sidebar.header("📉 Alert Settings")
delinquency_threshold = st.sidebar.number_input("Delinquency Threshold (%)", min_value=0.0, value=3.0, step=0.1)
manheim_threshold = st.sidebar.number_input("Monthly Decline Threshold (%)", min_value=0.0, value=1.5, step=0.1)

latest_delinquency = delinquency_df.iloc[-1]["value"] if not delinquency_df.empty else 0
latest_manheim = (manheim_df.iloc[-1]["value"] - manheim_df.iloc[-2]["value"]) / manheim_df.iloc[-2]["value"] * 100 if not manheim_df.empty else 0

st.sidebar.subheader("🔍 Indicator Interpretation")
st.sidebar.markdown(f"""
**Delinquency Rate:** {latest_delinquency:.2f}%
- {'⚠️ High risk of rising defaults' if latest_delinquency > delinquency_threshold else '🟡 Watching zone'}

**Used Car CPI Change:** {latest_manheim:.2f}%
- {'⚠️ Asset depreciation risk' if latest_manheim < -manheim_threshold else '🟡 No immediate threat'}
""")

if latest_delinquency > delinquency_threshold:
    st.sidebar.warning(f"⚠️ Delinquencies have exceeded {delinquency_threshold}%! Current: {latest_delinquency}%")

if latest_manheim < -manheim_threshold:
    st.sidebar.warning(f"⚠️ Manheim Index declined more than {manheim_threshold}%. Current: {latest_manheim:.2f}%")

st.markdown("## 📊 Strategy Recommendation")
if latest_delinquency > delinquency_threshold and latest_manheim < -manheim_threshold:
    st.success("🚨 All conditions triggered — consider starting a short position on subprime auto loan exposure.")
    st.markdown("**Suggested Actions:**")
    st.markdown("- Research put options on CACC, ALLY, or SC\n- Monitor auto ABS ETFs like HYG or JNK\n- Consider short exposure via SJB")
elif latest_delinquency > delinquency_threshold:
    st.warning("🟡 Delinquencies are elevated — prepare to monitor subprime lenders closely.")
else:
    st.info("✅ No immediate action. Stay in watch mode and monitor indicators.")

st.sidebar.info("Adjust alert thresholds to match your risk preferences.")
st.write("This dashboard tracks key auto loan ABS risk indicators and gives dynamic recommendations.")


from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.title("🥧 Interactive Pie Chart")
st.caption("Illustrative sample values for a class demo, not actual cooking records.")

CHART_TITLE = "Cuisine Mix"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pie_demo.csv"

# Read the CSV on each rerun so updates to the file are reflected in the chart.
df = pd.read_csv(DATA_PATH)

selected_cuisines = st.multiselect(
    "Choose cuisines",
    options=df["Cuisine"].tolist(),
    default=df["Cuisine"].tolist(),
)
show_donut = st.checkbox("Show as a donut chart")
filtered = df[df["Cuisine"].isin(selected_cuisines)]

if filtered.empty:
    st.info("Choose at least one cuisine to display the chart.")
else:
    fig = px.pie(
        filtered,
        names="Cuisine",
        values="Value",
        title=CHART_TITLE,
        hole=0.4 if show_donut else 0,
    )
    fig.update_traces(
        textinfo="label+percent",
        hovertemplate="%{label}<br>Value: %{value}<br>Share: %{percent}<extra></extra>",
    )
    st.plotly_chart(fig, width="stretch")

with st.expander("View CSV data"):
    st.dataframe(df, hide_index=True, width="stretch")

st.caption("Data source: data/pie_demo.csv. Percentages reflect the selected cuisines.")

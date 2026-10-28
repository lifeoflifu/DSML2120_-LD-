import pandas as pd
import plotly.express as px
import streamlit as st

from live_data import chart_times, denver_time, fetch_weather, rolling_history


st.set_page_config(page_title="Denver Weather | Lifu Deng", page_icon="🌤️", layout="wide")
st.title("🌤️ Denver Temperature Over Time")
st.caption("Open-Meteo weather for Denver: 39.7392° N, 104.9903° W.")

refresh_sec = st.slider("Refresh every (seconds)", 10, 120, 30, step=10)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
st.caption("The view can refresh every few seconds; API responses are reused for 10 minutes.")


@st.fragment(run_every=refresh_sec if auto_refresh else None)
def show_weather():
    st.button("Refresh view", key="weather_refresh")
    result, error = fetch_weather()
    if result is not None:
        st.session_state["weather_last_good"] = result
        mode = "API data"
    elif "weather_last_good" in st.session_state:
        result = st.session_state["weather_last_good"]
        mode = "Last successful API data"
        st.warning(f"Open-Meteo is unavailable. Showing the last successful response. {error}")
    else:
        mode = "SAMPLE DATA"
        st.warning(f"Open-Meteo is unavailable. The sample below is not live weather. {error}")

    if result is None:
        temperature, wind = 20.0, 10.0
    else:
        current = result["current"].iloc[0]
        temperature, wind = current["temperature"], current["wind"]
        st.caption(f"{mode} • recorded {denver_time(current['time'])} • fetched {denver_time(result['fetched_at'])}")

    columns = st.columns(2)
    suffix = " (sample)" if result is None else ""
    columns[0].metric("Temperature" + suffix, f"{temperature:.1f} °C")
    columns[1].metric("Wind speed" + suffix, f"{wind:.1f} km/h")

    incoming = pd.DataFrame(columns=["time", "temperature", "source"])
    if result is not None and error is None:
        current_points = result["current"][["time", "temperature"]].assign(source="Current weather")
        incoming = pd.concat([result["hourly"], current_points], ignore_index=True)
    history = rolling_history(st.session_state.get("weather_history"), incoming, keys=["time"], hours=6)
    st.session_state["weather_history"] = history

    if history.empty:
        st.info("The live temperature chart will appear when Open-Meteo responds. Sample values are not added to live history.")
    else:
        figure = px.line(chart_times(history), x="time", y="temperature", markers=True, hover_data=["source"], labels={"time": "Time (Denver)", "temperature": "Temperature (°C)", "source": "Source"}, title="Denver temperature · last 6 hours")
        st.plotly_chart(figure, width="stretch", key="weather_history_chart")
        st.caption("Starts with recent hourly model data, then adds distinct current-weather readings during this session. Repeated cached readings do not create extra points.")
        with st.expander("View temperature history"):
            st.dataframe(chart_times(history).rename(columns={"time": "Time (Denver)", "temperature": "Temperature (°C)", "source": "Source"}), hide_index=True, width="stretch")
    st.caption(f"View refreshed: {denver_time(pd.Timestamp.now(tz='UTC'))}. History belongs to this browser session.")


show_weather()
st.caption("Weather data: [Open-Meteo](https://open-meteo.com/) • AI assistance was used for guided learning and coding support.")

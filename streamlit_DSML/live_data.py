"""Cached API requests and rolling histories for the Lab 4.2 pages."""

import math

import pandas as pd
import requests
import streamlit as st


HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}
COINS = ["bitcoin", "ethereum"]
DENVER_TIMEZONE = "America/Denver"


def get_json(url, params):
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        detail = f" Retry-After: {retry_after}." if retry_after else ""
        raise ValueError(f"The API is rate-limiting requests (HTTP 429).{detail}")
    response.raise_for_status()
    return response.json()


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("The API returned a missing or invalid numeric value.")
    return result


def utc_timestamp(value, *, unit=None):
    result = pd.to_datetime(value, unit=unit, utc=True)
    if result is None or pd.isna(result):
        raise ValueError("The API returned a missing observation timestamp.")
    return result


@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices():
    """Reuse this response for five minutes, including a failed request."""
    try:
        data = get_json(
            "https://api.coingecko.com/api/v3/simple/price",
            {"ids": ",".join(COINS), "vs_currencies": "usd", "include_last_updated_at": "true"},
        )
        rows = []
        for coin in COINS:
            price = number(data[coin]["usd"])
            if price <= 0:
                raise ValueError("The API returned a nonpositive price.")
            rows.append({
                "coin": coin,
                "usd": price,
                "time": utc_timestamp(data[coin]["last_updated_at"], unit="s"),
            })
        return {"data": pd.DataFrame(rows), "fetched_at": pd.Timestamp.now(tz="UTC")}, None
    except (requests.RequestException, ValueError, TypeError, KeyError, OverflowError) as error:
        return None, str(error)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather():
    """Fetch current Denver weather and recent hourly model data; cache for ten minutes."""
    try:
        data = get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": 39.7392,
                "longitude": -104.9903,
                "current": "temperature_2m,wind_speed_10m",
                "hourly": "temperature_2m",
                "past_hours": 6,
                "forecast_hours": 1,
                "timezone": "UTC",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
        )
        current = data["current"]
        current_frame = pd.DataFrame([{
            "time": utc_timestamp(current["time"]),
            "temperature": number(current["temperature_2m"]),
            "wind": number(current["wind_speed_10m"]),
        }])
        hourly = pd.DataFrame({
            "time": pd.to_datetime(data["hourly"]["time"], utc=True),
            "temperature": [number(value) for value in data["hourly"]["temperature_2m"]],
            "source": "Hourly model data",
        })
        # Exclude forecasts beyond the current weather timestamp.
        hourly = hourly[hourly["time"] <= current_frame.iloc[0]["time"]]
        return {
            "current": current_frame,
            "hourly": hourly,
            "fetched_at": pd.Timestamp.now(tz="UTC"),
        }, None
    except (requests.RequestException, ValueError, TypeError, KeyError, OverflowError) as error:
        return None, str(error)


def rolling_history(previous, incoming, *, keys, hours, now=None):
    """Keep distinct provider observations in a real, bounded time window."""
    frames = [frame for frame in (previous, incoming) if frame is not None and not frame.empty]
    if not frames:
        return incoming.iloc[:0].copy()
    history = pd.concat(frames, ignore_index=True)
    history["time"] = pd.to_datetime(history["time"], utc=True)
    now = pd.Timestamp.now(tz="UTC") if now is None else pd.Timestamp(now)
    history = history.drop_duplicates(subset=keys, keep="last")
    history = history[history["time"].between(now - pd.Timedelta(hours=hours), now)]
    return history.sort_values("time").reset_index(drop=True)


def denver_time(timestamp):
    return pd.Timestamp(timestamp).tz_convert(DENVER_TIMEZONE).strftime("%b %d, %H:%M:%S %Z")


def chart_times(frame):
    """Use explicit Denver clock times on Plotly's time axis."""
    result = frame.copy()
    result["time"] = result["time"].dt.tz_convert(DENVER_TIMEZONE).dt.tz_localize(None)
    return result

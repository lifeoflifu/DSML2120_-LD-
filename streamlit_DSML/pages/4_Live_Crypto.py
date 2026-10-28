import pandas as pd
import plotly.express as px
import streamlit as st

from live_data import COINS, chart_times, denver_time, fetch_prices, rolling_history


st.set_page_config(page_title="Live Crypto | Lifu Deng", page_icon="📡", layout="wide")
st.title("📡 Live Crypto Prices")
st.caption("Bitcoin and Ethereum prices from CoinGecko, in US dollars.")

refresh_sec = st.slider("Refresh every (seconds)", 10, 120, 30, step=10)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
history_coin = st.selectbox("History for", COINS, format_func=str.title)
st.caption("The view can refresh every few seconds; API responses are reused for 5 minutes.")


@st.fragment(run_every=refresh_sec if auto_refresh else None)
def show_prices():
    # This button reruns the view without bypassing the API cache.
    st.button("Refresh view", key="crypto_refresh")
    result, error = fetch_prices()
    if result is not None:
        st.session_state["crypto_last_good"] = result
        mode = "API data"
    elif "crypto_last_good" in st.session_state:
        result = st.session_state["crypto_last_good"]
        mode = "Last successful API data"
        st.warning(f"CoinGecko is unavailable. Showing the last successful response. {error}")
    else:
        mode = "SAMPLE DATA"
        st.warning(f"CoinGecko is unavailable. Showing clearly labeled sample prices. {error}")

    if result is None:
        prices = pd.DataFrame([{"coin": "bitcoin", "usd": 68000}, {"coin": "ethereum", "usd": 3500}])
    else:
        prices = result["data"]
        st.caption(f"{mode} • fetched {denver_time(result['fetched_at'])}")

    columns = st.columns(2)
    for column, row in zip(columns, prices.itertuples(index=False)):
        column.metric(f"{row.coin.title()} ({'sample' if result is None else 'USD'})", f"${row.usd:,.2f}")
    comparison = px.bar(prices, x="coin", y="usd", color="coin", labels={"coin": "Coin", "usd": "Price (USD)"}, title=f"Current price comparison · {mode}")
    comparison.update_layout(showlegend=False)
    st.plotly_chart(comparison, width="stretch", key="crypto_comparison")

    # Samples are never inserted into the live history. Cached timestamps are deduplicated.
    incoming = prices if result is not None and error is None else pd.DataFrame(columns=["time", "coin", "usd"])
    history = rolling_history(st.session_state.get("crypto_history"), incoming, keys=["coin", "time"], hours=1)
    st.session_state["crypto_history"] = history
    st.subheader("Session price history · last 60 minutes")
    if history.empty:
        st.info("Live history will start when an API request succeeds.")
    else:
        view = history[history["coin"] == history_coin]
        figure = px.line(chart_times(view), x="time", y="usd", markers=True, labels={"time": "Time (Denver)", "usd": "Price (USD)"}, title=f"{history_coin.title()} · distinct API observations")
        st.plotly_chart(figure, width="stretch", key="crypto_history_chart")
        st.caption(f"{len(view)} distinct observation(s). One dot is expected at first; new points appear when CoinGecko provides a newer timestamp.")
    st.caption(f"View refreshed: {denver_time(pd.Timestamp.now(tz='UTC'))}. History belongs to this browser session.")


show_prices()
st.caption("Source: [CoinGecko](https://www.coingecko.com/) • AI assistance was used for guided learning and coding support.")

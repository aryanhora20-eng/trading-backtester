import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data import get_data
from strategy import moving_average_strategy
from backtest import backtest
from metrics import calculate_metrics
from stocks import NIFTY_50

# -----------------------
# Page Config
# -----------------------

st.set_page_config(page_title="Trading Dashboard", layout="wide")

st.title("📊 Quant Trading Dashboard")

# -----------------------
# Caching (Speed Boost)
# -----------------------

@st.cache_data
def cached_get_data(ticker):
    return get_data(ticker)

# -----------------------
# Functions
# -----------------------

def find_best_ma(ticker):
    best_sharpe = -999
    best_params = (50, 200)

    for short in [20, 30, 50, 70]:
        for long in [100, 150, 200, 250]:

            if short >= long:
                continue

            data = cached_get_data(ticker)
            data = moving_average_strategy(data, short, long)
            data = backtest(data)

            metrics = calculate_metrics(data)

            if metrics["Sharpe Ratio"] > best_sharpe:
                best_sharpe = metrics["Sharpe Ratio"]
                best_params = (short, long)

    return best_params


def generate_insights(metrics):
    insights = []

    if metrics["CAGR"] > 0.15:
        insights.append("🚀 Strong returns")
    elif metrics["CAGR"] > 0.08:
        insights.append("📈 Moderate returns")
    else:
        insights.append("⚠️ Low returns")

    if metrics["Drawdown"] < -0.4:
        insights.append("⚠️ High risk")
    elif metrics["Drawdown"] < -0.25:
        insights.append("⚖️ Moderate risk")
    else:
        insights.append("✅ Controlled risk")

    if metrics["Sharpe"] > 1:
        insights.append("💎 Excellent consistency")
    elif metrics["Sharpe"] > 0.5:
        insights.append("👍 Decent consistency")
    else:
        insights.append("⚠️ Weak consistency")

    return insights

# -----------------------
# Sidebar
# -----------------------

st.sidebar.header("⚙️ Strategy Settings")

scan_all = st.sidebar.checkbox("📡 Scan NIFTY 50")

tickers = st.sidebar.multiselect(
    "Select Stocks",
    NIFTY_50,
    default=NIFTY_50[:5]
)

if scan_all:
    tickers = NIFTY_50

short_window = st.sidebar.slider("Short MA", 10, 100, 50)
long_window = st.sidebar.slider("Long MA", 100, 300, 200)

optimize_button = st.sidebar.button("🧠 Suggest Best Strategy")
run_button = st.sidebar.button("🚀 Run Analysis")

# -----------------------
# Suggest MA
# -----------------------

if optimize_button and len(tickers) > 0:
    short_window, long_window = find_best_ma(tickers[0])
    st.sidebar.success(f"Suggested MA: {short_window}/{long_window}")

# -----------------------
# Run Analysis
# -----------------------

if run_button:

    if len(tickers) > 30:
        st.warning("Limiting to 30 stocks for performance")
        tickers = tickers[:30]

    results = []
    best_stock = None
    best_data = None
    best_sharpe = -999

    with st.spinner("Scanning market..."):

        for ticker in tickers:
            data = cached_get_data(ticker)
            data = moving_average_strategy(data, short_window, long_window)
            data = backtest(data)

            metrics = calculate_metrics(data)

            results.append({
                "Stock": ticker,
                "CAGR": metrics["CAGR"],
                "Drawdown": metrics["Max Drawdown"],
                "Sharpe": metrics["Sharpe Ratio"]
            })

            if metrics["Sharpe Ratio"] > best_sharpe:
                best_sharpe = metrics["Sharpe Ratio"]
                best_stock = ticker
                best_data = data.copy()

    df = pd.DataFrame(results)

    # -----------------------
    # Bloomberg-style KPI
    # -----------------------

    st.markdown("### 📊 Market Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("🏆 Best Stock", best_stock)
    col2.metric("📈 Sharpe", f"{best_sharpe:.2f}")
    col3.metric("📊 Stocks", len(tickers))

    st.markdown("---")

    # -----------------------
    # Leaderboard
    # -----------------------

    st.markdown("### 🥇 Top Opportunities")

    top3 = df.sort_values(by="Sharpe", ascending=False).head(3)

    for i, row in top3.iterrows():
        st.write(
            f"{row['Stock']} | Sharpe: {row['Sharpe']:.2f} | CAGR: {row['CAGR']:.2%}"
        )

    # -----------------------
    # Full Table
    # -----------------------

    st.markdown("### 📋 Full Market Scan")

    st.dataframe(df, use_container_width=True)

    # -----------------------
    # Insights
    # -----------------------

    st.markdown("### 🧠 Insights")

    best_metrics = df[df["Stock"] == best_stock].iloc[0]

    for insight in generate_insights(best_metrics):
        st.success(insight)

    # -----------------------
    # Signal Indicator
    # -----------------------

    latest_signal = best_data['Signal'].iloc[-1]

    if latest_signal == 1:
        st.success(f"📢 BUY Signal for {best_stock}")
    elif latest_signal == -1:
        st.error(f"📢 SELL Signal for {best_stock}")
    else:
        st.warning("No clear signal")

    # -----------------------
    # Chart
    # -----------------------

    best_data['BuyHold'] = (best_data['Close'] / best_data['Close'].iloc[0]) * 10000
    best_data['Strategy_norm'] = best_data['Portfolio'] / best_data['Portfolio'].iloc[0]
    best_data['BuyHold_norm'] = best_data['BuyHold'] / best_data['BuyHold'].iloc[0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=best_data.index,
        y=best_data['Strategy_norm'],
        name="Strategy",
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=best_data.index,
        y=best_data['BuyHold_norm'],
        name="Market",
        line=dict(width=3)
    ))

    fig.update_layout(
        template="plotly_dark",
        title=f"{best_stock} Performance",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
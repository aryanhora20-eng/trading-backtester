from data import get_data
from strategy import moving_average_strategy
from backtest import backtest
from metrics import calculate_metrics
import matplotlib.pyplot as plt

# -----------------------
# STEP 1: Optimization (on RELIANCE)
# -----------------------

ticker = "RELIANCE.NS"

best_result = None
best_params = None
best_data = None

for short in [20, 50, 100]:
    for long in [100, 200, 300]:

        if short >= long:
            continue

        data = get_data(ticker)
        data = moving_average_strategy(data, short, long)
        data = backtest(data)

        metrics = calculate_metrics(data)

        # Select best based on Sharpe Ratio
        if best_result is None or metrics["Sharpe Ratio"] > best_result["Sharpe Ratio"]:
            best_result = metrics
            best_params = (short, long)
            best_data = data.copy()

# -----------------------
# STEP 2: Print Best Result
# -----------------------

print("\nBest Strategy Found (RELIANCE):")
print(f"Short MA: {best_params[0]}, Long MA: {best_params[1]}")

print("\nPerformance Metrics:")
for key, value in best_result.items():
    print(f"{key}: {value:.4f}")

# -----------------------
# STEP 3: Plot Best Strategy
# -----------------------

best_data['BuyHold'] = (best_data['Close'] / best_data['Close'].iloc[0]) * 10000

plt.figure(figsize=(12,6))
plt.plot(best_data['Portfolio'], label='Best Strategy')
plt.plot(best_data['BuyHold'], label='Buy & Hold')

plt.legend()
plt.title(f"Best Strategy vs Buy & Hold ({ticker})")
plt.show()

# -----------------------
# STEP 4: Multi-Stock Validation
# -----------------------

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

print("\nMulti-Stock Validation Results:")

for t in tickers:
    data = get_data(t)
    data = moving_average_strategy(data, best_params[0], best_params[1])
    data = backtest(data)

    metrics = calculate_metrics(data)

    print(f"\n{t}")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

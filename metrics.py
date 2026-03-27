import numpy as np

def calculate_metrics(data):
    portfolio = data['Portfolio']

    returns = portfolio.pct_change().dropna()

    total_days = len(portfolio)
    years = total_days / 252

    cagr = (portfolio.iloc[-1] / portfolio.iloc[0]) ** (1 / years) - 1

    peak = portfolio.cummax()
    drawdown = (portfolio - peak) / peak
    max_drawdown = drawdown.min()

    sharpe = (returns.mean() / returns.std()) * np.sqrt(252)

    return {
        "CAGR": cagr,
        "Max Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe
    }
import yfinance as yf
import pandas as pd

def get_data(ticker, start="2015-01-01", end="2024-01-01"):
    data = yf.download(ticker, start=start, end=end)

    # Flatten columns if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data[['Close']].copy()
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

    data.dropna(inplace=True)

    return data
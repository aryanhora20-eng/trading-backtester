import yfinance as yf
import pandas as pd

def get_data(ticker, start="2015-01-01", end="2024-01-01"):
    data = yf.download(ticker, start=start, end=end)

    # If no data returned
    if data is None or data.empty:
        return None

    # Flatten columns if multi-index
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Ensure Close exists
    if 'Close' not in data.columns:
        return None

    data = data[['Close']].copy()
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

    data.dropna(inplace=True)

    # Final check
    if data.empty:
        return None

    return data
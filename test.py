import yfinance as yf

data = yf.download("RELIANCE.NS", start="2020-01-01")
print(data.head())

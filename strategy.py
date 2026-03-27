import pandas as pd

def moving_average_strategy(data, short_window=50, long_window=200):

    data['MA_short'] = data['Close'].rolling(window=short_window).mean()
    data['MA_long'] = data['Close'].rolling(window=long_window).mean()

    data['Trend_Strength'] = (data['MA_short'] - data['MA_long']) / data['MA_long']

    data['Signal'] = 0

    data.loc[
        (data['MA_short'] > data['MA_long']) & (data['Trend_Strength'] > 0.02),
        'Signal'
    ] = 1

    data.loc[
        (data['MA_short'] < data['MA_long']) | (data['Trend_Strength'] < 0.01),
        'Signal'
    ] = -1

    return data
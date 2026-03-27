def backtest(data, initial_capital=10000):
    capital = float(initial_capital)
    position = 0
    entry_price = 0.0
    position_size = 0.5

    transaction_cost = 0.001
    stop_loss_pct = 0.10

    portfolio_values = []

    for i in range(len(data)):
        signal = int(data['Signal'].iloc[i])
        price = float(data['Close'].iloc[i])

        # BUY
        if signal == 1 and position == 0:
            position = 1
            entry_price = price * (1 + transaction_cost)

        # SELL / STOP LOSS
        elif position == 1:

            if price < entry_price * (1 - stop_loss_pct):
                exit_price = price * (1 - transaction_cost)
                capital = capital * (1 + position_size * ((exit_price / entry_price) - 1))
                position = 0

            elif signal == -1:
                exit_price = price * (1 - transaction_cost)
                capital = capital * (1 + position_size * ((exit_price / entry_price) - 1))
                position = 0

        # Portfolio tracking
        if position == 1:
            current_value = capital * (1 + position_size * ((price / entry_price) - 1))
        else:
            current_value = capital

        portfolio_values.append(float(current_value))

    data['Portfolio'] = portfolio_values

    return data
def execute_strategy(data, capital):
    gap = (data['open'] - data['prev_close']) / data['prev_close']

    # Step 1: Reversal
    if gap < 0:
        direction1 = "CALL"
    elif gap > 0:
        direction1 = "PUT"
    else:
        return capital, "NO TRADE"

    move = (data['close'] - data['open']) / data['open']

    # Determine trend
    trend = "CALL" if move > 0 else "PUT"

    # Convert to option-like move
    def get_option_move(direction):
        m = move
        if direction == "PUT":
            m = -m
        return m * 5

    # Step 1 (10%)
    option_move1 = get_option_move(direction1)

    if option_move1 >= 0.17:
        profit = capital * 0.10 * 0.17
        capital += profit
        return capital, f"{direction1} | Step1 WIN"

    # Step 2 (30%) → SWITCH TO TREND
    option_move2 = get_option_move(trend)

    if option_move2 >= 0.17:
        profit = capital * 0.40 * 0.17
        capital += profit
        return capital, f"{trend} | Step2 WIN"

    # Step 3 (60%) → CONTINUE TREND
    option_move3 = get_option_move(trend)

    if option_move3 >= 0.17:
        profit = capital * 1.0 * 0.17
        capital += profit
        return capital, f"{trend} | Step3 WIN"

    # If everything fails
    capital = 0
    return capital, f"{trend} | FULL LOSS"

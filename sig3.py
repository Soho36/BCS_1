import pandas as pd
"""
GPT version with timestamps to avoid generating signals before level discovery
"""


def level_rejection_signals(df, sr_levels_out, lookback=3):
    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)
    print('8. DATAFRAME INSIDE level_rejection_signals(df): \n', df)

    # Track the condition of level crosses over `lookback` period
    level_cross_trackers = {i: {"above": 0, "below": 0} for i in range(1, len(sr_levels_out) + 1)}

    for index, row in df.iterrows():
        if index == 0:
            # Skip the first row since there's no previous row for comparison
            rejection_signals_with_prices.append((None, None))
            rejection_signals_for_chart.append(None)
            continue

        previous_close = df.iloc[index - 1]['Close']
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']

        signal = None  # Reset signal for each row
        price_level = None

        # Iterate over all levels and check conditions
        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]
            if current_sr_level is not None:
                tracker = level_cross_trackers[level_column]

                # Update trackers for cross events
                if previous_close < current_sr_level and current_candle_high > current_sr_level:
                    tracker["above"] += 1
                elif previous_close > current_sr_level and current_candle_low < current_sr_level:
                    tracker["below"] += 1

                # If the opposite condition happens, reset the tracker
                if previous_close > current_sr_level:
                    tracker["above"] = 0
                if previous_close < current_sr_level:
                    tracker["below"] = 0

                # Check if the level has been crossed multiple times within the lookback period
                if tracker["above"] > 0 and tracker["above"] <= lookback and current_candle_close < current_sr_level:
                    signal = -100
                    price_level = current_sr_level
                    tracker["above"] = 0  # Reset after signal
                    break

                if tracker["below"] > 0 and tracker["below"] <= lookback and current_candle_close > current_sr_level:
                    signal = 100
                    price_level = current_sr_level
                    tracker["below"] = 0  # Reset after signal
                    break

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

# Example usage:
# lookback = 5 (can be adjusted as needed)
# df is your input DataFrame
# sr_levels_out is your list of levels



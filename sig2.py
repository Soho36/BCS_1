import pandas as pd


def level_rejection_signals(df, sr_levels_out, use_level_price_as_entry, use_candle_close_as_entry):
    # Extract the price levels from `sr_levels_out` and track whether the price has crossed above each level
    price_levels = [level[1] for level in sr_levels_out]
    crossed_above_level = {level: False for level in price_levels}

    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)
    print('8. DATAFRAME INSIDE level_rejection_signals(df): \n', df)  # .iloc[0:50]

    for index, row in df.iterrows():
        if index == 0:  # Skip the first row as there's no previous close
            rejection_signals_with_prices.append((None, None))
            rejection_signals_for_chart.append(None)
            continue

        previous_close = df.iloc[index - 1]['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_close = row['Close']

        signal = None  # Reset signal for each row
        price_level = None

        for current_sr_level in price_levels:
            if pd.notna(current_sr_level):  # Ensure the level is not NaN

                # Check if the previous close was below the resistance level and price crossed above
                if not crossed_above_level[current_sr_level] and previous_close < current_sr_level:
                    if current_candle_high > current_sr_level:  # Price has crossed above resistance level
                        crossed_above_level[current_sr_level] = True  # Set flag that the level has been crossed

                # If the price has previously crossed above the resistance level, we check for it to fall below
                if crossed_above_level[current_sr_level]:
                    if current_candle_close < current_sr_level:  # Price has dropped below the level
                        signal = -100
                        price_level = current_sr_level
                        break

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

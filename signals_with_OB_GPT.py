import pandas as pd


def level_rejection_signals(df, sr_levels_out):

    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)

    for index, row in df.iterrows():

        previous_close = df.iloc[index - 1]['Close'] if index > 0 else None  # Handle first row case
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']

        signal = None  # Reset signal for each row
        price_level = None

        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]
            if current_sr_level is not None:

                # Check for short signal: over-under condition
                if previous_close is not None and previous_close < current_sr_level:   # Previous candle close was below the level
                    if current_candle_high > current_sr_level and current_candle_close < current_sr_level:
                        # Over-Under condition met
                        signal_candle_close = current_candle_close  # Store signal candle close

                        # Loop through subsequent candles for confirmation (find first green candle)
                        for subsequent_index in range(index + 1, len(df)):
                            subsequent_row = df.iloc[subsequent_index]
                            if subsequent_row['Close'] > subsequent_row['Open']:  # First green candle found
                                green_candle_low = subsequent_row['Low']

                                # Wait for price to hit the low of the first green candle
                                for next_index in range(subsequent_index + 1, len(df)):
                                    next_row = df.iloc[next_index]  # Correctly accessing rows
                                    if next_row['Low'] <= green_candle_low:
                                        signal = -100  # Short signal
                                        price_level = green_candle_low  # Enter at the low of the first green candle
                                        break
                                break
                        break

                # Long signal logic here (under-over) - not mentioned for short signal, so it's omitted

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

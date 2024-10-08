import pandas as pd


def level_rejection_signals(df, sr_levels_out):

    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)

    for index, row in df.iterrows():
        # if index == 0:
        #     continue  # Skip the first row since we need a previous candle for comparison

        previous_close = df.iloc[index - 1]['Close']
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']

        signal = None  # Reset signal for each row
        price_level = None

        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]
            if current_sr_level is not None:

                # Check for short signal: over-under condition
                if previous_close < current_sr_level:   # Previous candle close was below the level
                    if current_candle_high > current_sr_level:  # Current candle crossed above the level
                        if current_candle_close < current_sr_level:  # but closed below
                            signal_candle_close = current_candle_close  # Store signal candle close
                            # Loop through subsequent candles for confirmation
                            for subsequent_index in range(index + 1, len(df)):
                                subsequent_row = df.iloc[subsequent_index]
                                if subsequent_row['Close'] < signal_candle_close:  # Confirming condition: next close below signal candle
                                    signal = -100
                                    price_level = current_sr_level
                                    break
                            break

                # Check for long signal: under-over condition
                elif previous_close > current_sr_level:   # Previous close was above the level
                    if current_candle_low < current_sr_level:  # Price crossed below the level
                        if current_candle_close > current_sr_level:  # but closed above
                            signal_candle_close = current_candle_close  # Store signal candle close
                            # Loop through subsequent candles for confirmation
                            for subsequent_index in range(index + 1, len(df)):
                                subsequent_row = df.iloc[subsequent_index]
                                if subsequent_row['Close'] > signal_candle_close:  # Confirming condition: next close above signal candle
                                    signal = 100
                                    price_level = current_sr_level
                                    break
                            break

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

import pandas as pd
"""
GPT version with timestamps to avoid generating signals before level discovery
"""


def level_rejection_signals(df, sr_levels_out):

    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    # Track the discovery time of each level
    level_discovery_time = {level: None for _, level in sr_levels_out}

    df.reset_index(inplace=True)
    print('8. DATAFRAME INSIDE level_rejection_signals(df): \n', df)  # .iloc[0:50]

    for index, row in df.iterrows():
        current_time = row['DateTime']  # Assuming there's a 'Timestamp' column in your DataFrame
        previous_close = df.iloc[index - 1]['Close']
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']

        signal = None  # Reset signal for each row
        price_level = None

        for level_index, (level_idx, current_sr_level) in enumerate(sr_levels_out):
            if pd.notna(current_sr_level):  # Ensure the level is not NaN

                # Set the discovery time if it hasn't been set yet
                if level_discovery_time[current_sr_level] is None:
                    level_discovery_time[current_sr_level] = current_time

                # Ensure the current row is after the level discovery time
                if current_time >= level_discovery_time[current_sr_level]:
                    if previous_close < current_sr_level:  # Check if the PREVIOUS CANDLE close was below the level
                        if current_candle_high > current_sr_level:  # CURRENT CANDLE has crossed above the level
                            if current_candle_close < current_sr_level:  # but closed below
                                signal = -100
                                price_level = current_sr_level
                                break

                    elif previous_close > current_sr_level:  # Check if the previous close was above the support level
                        if current_candle_low < current_sr_level:  # Price has crossed below support level
                            if current_candle_close > current_sr_level:  # but closed above
                                signal = 100
                                price_level = current_sr_level
                                break

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

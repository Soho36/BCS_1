import pandas as pd


def level_rejection_signals(df, sr_levels_out, use_level_price_as_entry, use_candle_close_as_entry):

    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)
    print('8. DATAFRAME INSIDE level_rejection_signals(df): \n', df)    # .iloc[0:50]

    for index, row in df.iterrows():
        previous_close = df.iloc[index - 1]['Close']
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']

        signal = None  # Reset signal for each row
        price_level = None
        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]
            if current_sr_level is not None:
                if previous_close < current_sr_level:   # Check if the PREVIOUS CANDLE close was below the level
                    if current_candle_high > current_sr_level:    # CURRENT CANDLE has crossed above the level
                        if use_level_price_as_entry:    # If limit order from level
                            signal = -100
                            price_level = current_sr_level
                            break
                        elif use_candle_close_as_entry:     # If market order when CURRENT CANDLE closed below
                            if current_candle_close < current_sr_level:  # but closed below
                                signal = -100
                                break

                elif previous_close > current_sr_level:   # Check if the previous close was above the support level
                    if current_candle_low < current_sr_level:    # Price has crossed below support level
                        if use_level_price_as_entry:
                            signal = 100
                            price_level = current_sr_level
                            break
                        elif use_candle_close_as_entry:
                            if current_candle_close > current_sr_level:  # but closed above
                                signal = 100
                                break

        rejection_signals_with_prices.append((signal, price_level))
        rejection_signals_for_chart.append(signal)

    # print('Rejection_signals: \n', rejection_signals_with_prices)
    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart


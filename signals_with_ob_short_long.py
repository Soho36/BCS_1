import pandas as pd


def level_rejection_signals(output_df_with_levels, sr_levels_out, over_under_threshold):
    rejection_signals_with_prices = []
    rejection_signals_for_chart = []
    ob_candle_for_chart = []
    over_under_for_chart = []

    # Create a dictionary to track signal count per level
    level_signal_count = {i: 0 for i in range(1, len(sr_levels_out) + 1)}

    # Explicitly define which levels are resistance and which are support
    # level_type = {i: 'resistance' if i % 2 != 0 else 'support' for i in range(1, len(sr_levels_out) + 1)}

    output_df_with_levels.reset_index(inplace=True)

    for index, row in output_df_with_levels.iterrows():
        previous_close = output_df_with_levels.iloc[index - 1]['Close'] if index > 0 else None
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_low = row['Low']
        current_candle_time = row['Time']

        print(f"---\nAnalyzing candle at index {index}, "
              f"Time: {current_candle_time}, "
              f"Close: {current_candle_close}, "
              f"High: {current_candle_high}, "
              f"Low: {current_candle_low}")

        signal = None  # Reset signal for each row
        ob_signal = None
        price_level = None
        signal_index = None  # Initialize signal_index
        subsequent_index = None  # Initialize subsequent_index
        over_under_signal = None

        # Loop through each level column
        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]

            if current_sr_level is not None:
                # Check if signal count for this level has reached the threshold
                if level_signal_count[level_column] < over_under_threshold:
                    # Resistance level logic (only for short signals)
                    # if level_type[level_column] == 'resistance':
                    if previous_close is not None and previous_close < current_sr_level:  # Previous close was below level
                        if current_candle_high > current_sr_level:
                            if current_candle_close < current_sr_level:
                                # Over-Under condition met for short
                                over_under_signal = -100
                                level_signal_count[level_column] += 1
                                print(f"Short: Over-under condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # (Your existing short trade logic continues here)
                                # Step 1: Find the first green candle (where close > open)
                                green_candle_found = False
                                green_candle_low = None

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):
                                    subsequent_row = output_df_with_levels.iloc[subsequent_index]
                                    subsequent_time = subsequent_row['Time']
                                    if subsequent_row['Close'] > subsequent_row['Open']:  # First green candle found
                                        if subsequent_row['Close'] < current_sr_level:  # Candle must be under the level
                                            green_candle_low = subsequent_row['Low']
                                            green_candle_found = True
                                            ob_signal = -100
                                            print(f"Short: GREEN candle found and valid at index {subsequent_index}, "
                                                  f"Time: {subsequent_time}, "
                                                  f"Low: {green_candle_low}")
                                            break

                                # Step 2: After finding the green candle, wait for the price to hit its low
                                if green_candle_found:
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_row = output_df_with_levels.iloc[next_index]
                                        if next_row['Close'] < green_candle_low:  # Price hits the low of the green candle
                                            signal = -100  # Short signal
                                            price_level = next_row['Close']
                                            signal_index = next_index
                                            print(f"Short: Signal triggered at index {next_index}, "
                                                  f"Price level: {price_level}")
                                            break
                                        elif next_row['Close'] > next_row['Open']:
                                            green_candle_low = next_row['Low']
                                            print(f"Short: New green candle formed at index {next_index}, "
                                                  f"New Target Low: {green_candle_low}")
                                            subsequent_index = next_index
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

                    # Support level logic (only for long signals)
                    # if level_type[level_column] == 'support':
                    if previous_close is not None and previous_close > current_sr_level:  # Previous close was above level
                        if current_candle_low < current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Under-Over condition met for long
                                over_under_signal = 100
                                level_signal_count[level_column] += 1
                                print(f"Long: Under-over condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):
                                    subsequent_row = output_df_with_levels.iloc[subsequent_index]
                                    subsequent_time = subsequent_row['Time']
                                    if subsequent_row['Close'] < subsequent_row['Open']:  # First red candle found
                                        if subsequent_row['Close'] > current_sr_level:  # Candle must be above the level
                                            red_candle_high = subsequent_row['High']
                                            red_candle_found = True
                                            ob_signal = 100
                                            print(f"Long: RED candle found and valid at index {subsequent_index}, "
                                                  f"Time: {subsequent_time}, "
                                                  f"High: {red_candle_high}")
                                            break

                                # Step 2: After finding the red candle, wait for the price to hit its high
                                if red_candle_found:
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_row = output_df_with_levels.iloc[next_index]
                                        if next_row['Close'] > red_candle_high:  # Price hits the high of the red candle
                                            signal = 100  # Long signal
                                            price_level = next_row['Close']
                                            signal_index = next_index
                                            print(f"Long: Signal triggered at index {next_index}, "
                                                  f"Price level: {price_level}")
                                            break
                                        elif next_row['Close'] < next_row['Open']:
                                            red_candle_high = next_row['High']
                                            print(f"Long: New red candle formed at index {next_index}, "
                                                  f"New Target High: {red_candle_high}")
                                            subsequent_index = next_index
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

            # Append values with None for signals not triggered
        rejection_signals_with_prices.append((signal_index, signal, price_level))
        rejection_signals_for_chart.append((signal_index, signal))
        ob_candle_for_chart.append((subsequent_index, ob_signal))
        over_under_for_chart.append((index, over_under_signal))
    else:
        print(f"Max signals for level {level_column} reached")

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    ob_candle_series_for_chart = pd.Series(ob_candle_for_chart)
    over_under_series_for_chart = pd.Series(over_under_for_chart)
    return (rejection_signals_series_with_prices,
            rejection_signals_series_for_chart,
            ob_candle_series_for_chart,
            over_under_series_for_chart,
            level_signal_count)

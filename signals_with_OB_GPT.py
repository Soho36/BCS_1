import pandas as pd


def level_rejection_signals(output_df_with_levels, sr_levels_out, over_under_threshold):
    rejection_signals_with_prices = []
    rejection_signals_for_chart = []
    ob_candle_for_chart = []
    over_under_for_chart = []

    # Create a dictionary to track signal count per level
    level_signal_count = {i: 0 for i in range(1, len(sr_levels_out) + 1)}

    output_df_with_levels.reset_index(inplace=True)

    for index, row in output_df_with_levels.iterrows():
        previous_close = output_df_with_levels.iloc[index - 1]['Close'] if index > 0 else None  # Handle first row case
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_time = row['Time']

        print(f"---\nAnalyzing candle at index {index}, "
              f"Time: {current_candle_time}, "
              f"Close: {current_candle_close}, "
              f"High: {current_candle_high}")

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

                    # Check for short signal: over-under condition
                    if previous_close is not None and previous_close < current_sr_level:  # Previous close was below level
                        if current_candle_high > current_sr_level:
                            if current_candle_close < current_sr_level:
                                # Over-Under condition met
                                over_under_signal = -100
                                level_signal_count[level_column] += 1  # Increment counter for this level
                                print(f"Over-under condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first green candle (where close > open)
                                green_candle_found = False
                                green_candle_low = None

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):
                                    subsequent_row = output_df_with_levels.iloc[subsequent_index]
                                    subsequent_time = subsequent_row['Time']  # Time for the subsequent row
                                    print(f"Looking for GREEN candle at index {subsequent_index}, "
                                          f"Time: {subsequent_time}, Close: {subsequent_row['Close']}, "
                                          f"Open: {subsequent_row['Open']}")
                                    if subsequent_row['Close'] > subsequent_row['Open']:  # First green candle found
                                        print(f"GREEN candle found at index {subsequent_index}, "
                                              f"Time: {subsequent_time}, ")

                                        if subsequent_row['Close'] < current_sr_level:  # Candle must be under the level
                                            green_candle_low = subsequent_row['Low']
                                            green_candle_found = True
                                            ob_signal = -100
                                            print(f"And it is valid. Creating the signal at index: {subsequent_index}, "
                                                  f"Time: {subsequent_time}, "
                                                  f"Low: {green_candle_low}")

                                            break  # Exit loop after finding the first green candle
                                        else:
                                            print(f"But it is not below the level. Checking next candle...")

                                # Step 2: After finding the green candle, wait for the price to hit its low
                                if green_candle_found:
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_row = output_df_with_levels.iloc[next_index]
                                        next_time = next_row['Time']  # Use the correct time for the next row
                                        print(
                                            f"Waiting for next candle to close under GREEN candle low at {next_index},"
                                            f"Time: {next_time}, "
                                            f"Low: {next_row['Low']}")
                                        if next_row[
                                            'Close'] < green_candle_low:  # Price hits the low of the green candle
                                            signal = -100  # Short signal
                                            price_level = next_row[
                                                'Close']  # Enter at the low of the first green candle
                                            signal_index = next_index  # Assign signal_index here
                                            print(f"It did. Signal triggered at index {next_index}, "
                                                  f"Time: {next_time}, "
                                                  f"Price level: {price_level}")
                                            break
                                        elif next_row['Close'] > next_row['Open']:
                                            green_candle_low = next_row['Low']
                                            print(f"New green candle formed at index {next_index},"
                                                  f"Time: {next_time}, "
                                                  f"New Target Low: {green_candle_low}")
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

import pandas as pd


def level_rejection_signals(output_df_with_levels, sr_levels_out, over_under_threshold, max_time_waiting_for_entry):
    rejection_signals_with_prices = []
    yellow_star_signals_with_prices = []
    rejection_signals_for_chart = []
    ob_candle_for_chart = []
    level_interaction_signal_for_chart = []

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

        print(
            f"---\nAnalyzing candle at index {index}, "
            f"Time: {current_candle_time}, "
        )

        signal = None  # Reset signal for each row
        ob_signal = None
        price_level = None
        signal_index = None  # Initialize signal_index
        subsequent_index = None  # Initialize subsequent_index
        level_interaction_signal = None
        stop_price = None

        # Loop through each level column
        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]

            if current_sr_level is not None:
                # Check if signal count for this level has reached the threshold
                if level_signal_count[level_column] < over_under_threshold:

                    # **************************************************************************************************
                    # SHORTS LOGICS BEGIN HERE
                    # **************************************************************************************************
                    # REJECTION SHORTS LOGIC:
                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_high > current_sr_level:
                            if current_candle_close < current_sr_level:
                                # Over-Under condition met for short
                                level_interaction_signal = -100
                                level_signal_count[level_column] += 1
                                print(f"Short: 'Over-under' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first green candle (where close > open)
                                green_candle_found = False
                                green_candle_low = None
                                # looking_for_signal_counter = 0  # Initialize the counter here

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    potential_ob_time = potential_ob_candle['Time']
                                    print(
                                        f"Looking for GREEN candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )
                                    # First green candle found
                                    if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                        print(
                                            f"Last GREEN candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Candle must be under the level
                                        if potential_ob_candle['Close'] < current_sr_level:
                                            green_candle_low = potential_ob_candle['Low']
                                            green_candle_found = True
                                            ob_signal = -100
                                            print(
                                                f"It's below the level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(f"But we are not below the level. Checking next candle...")

                                # Step 2: After finding the green candle, wait for the price to hit its low
                                if green_candle_found:
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']
                                        print(
                                            f"Waiting for next candle to close under GREEN candle low at {next_index},"
                                            f"Time: {signal_time}"
                                        )
                                        # Price hits the low of the green candle
                                        if next_candle_after_ob['Close'] < green_candle_low:
                                            if next_candle_after_ob['Close'] < current_sr_level:
                                                signal = -100  # Short signal
                                                signal_index = next_index
                                                price_level = next_candle_after_ob['Close']

                                                print(
                                                    f"Signal triggered at index {next_index}, "
                                                    f"Time: {signal_time}, "
                                                    f"Candle closing price: {price_level}"
                                                )
                                                break
                                            else:
                                                print(
                                                    f"It closed under, but we are not under the level."
                                                    f" Checking next candle..."
                                                )
                                        elif next_candle_after_ob['Close'] > next_candle_after_ob['Open']:
                                            signal_time = next_candle_after_ob['Time']
                                            green_candle_low = next_candle_after_ob['Low']
                                            stop_price = next_candle_after_ob['High']
                                            print(
                                                f"NEW GREEN candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated


#                   BR-D LOGIC BEGIN HERE ******************************************************************************
                    # Previous close was above level
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_close < current_sr_level:
                            # Over condition met for short
                            level_interaction_signal = -100
                            level_signal_count[level_column] += 1
                            level_interaction_signal_time = current_candle_time

                            print(f"Short: 'Under' condition met at index {index}, "
                                  f"Time: {current_candle_time}, "
                                  f"SR level: {current_sr_level}")

                            # Step 1: Find the first green candle (where close > open)
                            green_candle_found = False
                            green_candle_low = None

                            for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                potential_ob_time = pd.to_datetime(
                                    potential_ob_candle['Time'])  # Convert to datetime for time calculations

                                # Calculate time difference between the current potential candle and the initial SR level interaction
                                time_diff = (potential_ob_time - pd.to_datetime(
                                    level_interaction_signal_time)).total_seconds() / 60

                                # Check if we've exceeded the maximum waiting time
                                if time_diff > max_time_waiting_for_entry:
                                    print(
                                        f"Exceeded {max_time_waiting_for_entry}-minute window while looking for green candle at index {subsequent_index}, "
                                        f"Level interaction time: {level_interaction_signal_time}, "
                                        f"Time diff: {time_diff} minutes"
                                    )
                                    break  # Exit the loop if time limit is exceeded

                                print(
                                    f"Looking for GREEN candle at index {subsequent_index}, "
                                    f"Time: {potential_ob_time}"
                                )

                                # Check if it's a green candle (close > open)
                                if potential_ob_candle['Close'] > potential_ob_candle['Open']:
                                    print(
                                        f"GREEN candle found at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )

                                    # Check if the green candle is below the SR level
                                    if potential_ob_candle['Close'] < current_sr_level:
                                        green_candle_low = potential_ob_candle['Low']
                                        green_candle_found = True
                                        ob_signal = -100  # Set short signal
                                        print(
                                            f"Green candle is below the SR level at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        break  # Exit the loop, as we have found the valid green candle below the level

                                    else:
                                        print(
                                            f"Green candle found, but it's not below the level. Checking next candle...")

                            # Step 2: After finding the green candle, wait for the price to hit its low
                            if green_candle_found:
                                potential_ob_time = pd.to_datetime(potential_ob_time)  # Store the time of the green candle
                                for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                    next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                    signal_time = next_candle_after_ob['Time']
                                    # Calculate the time difference in minutes between the green candle and the current candle
                                    time_diff = (potential_ob_time -
                                                 pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

                                    print(
                                        f"Waiting for next candle to close below GREEN candle low at {next_index}, "
                                        f"Time: {signal_time}"
                                    )
                                    if time_diff > max_time_waiting_for_entry:
                                        print(
                                            f"Stopping search: "
                                            f"1Exceeded {max_time_waiting_for_entry}-minute window after GREEN candle at index {next_index}, \n"
                                            f"Level_interaction_signal_time: {level_interaction_signal_time}\n"
                                            f"Green_candle_time: {potential_ob_time}\n"
                                            f"time_diff: {time_diff}"
                                        )
                                        break
                                    if next_candle_after_ob['Close'] < green_candle_low:
                                        # Price hits the low of the green candle
                                        if next_candle_after_ob['Close'] < current_sr_level:
                                            signal = -100  # Short signal
                                            signal_index = next_index
                                            price_level = next_candle_after_ob['Close']

                                            print(
                                                f"Signal triggered at index {next_index}, "
                                                f"Time: {signal_time}, "
                                                f"Candle closing price: {price_level}"
                                            )
                                            break
                                        else:
                                            print(
                                                f"It closed below, but we are not below the level. "
                                                f"Checking next candle..."
                                            )

                                    elif next_candle_after_ob['Close'] > next_candle_after_ob['Open']:
                                        next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                        signal_time = next_candle_after_ob['Time']
                                        green_candle_low = next_candle_after_ob['Low']
                                        stop_price = next_candle_after_ob['High']
                                        print(
                                            f"NEW GREEN candle formed at index {next_index}, "
                                            f"Time: {signal_time}, "
                                        )
                                        subsequent_index = next_index
                                        time_diff = (next_candle_after_ob_time -
                                                     pd.to_datetime(
                                                         level_interaction_signal_time)).total_seconds() / 60
                                        if time_diff > max_time_waiting_for_entry:
                                            print(
                                                f"Stopping search: "
                                                f"2Exceeded {max_time_waiting_for_entry}-minute window after GREEN candle at index {next_index}, \n"
                                                f"Signal_time: {level_interaction_signal_time}\n"
                                                f"Green_candle_time: {next_candle_after_ob_time}\n"
                                                f"time_diff: {time_diff}"
                                            )
                                            break
                                break  # Exit the level loop once a signal is generated
                            else:
                                print('Waiting for green candle...')
                        else:
                            print('current_candle_close < current_sr_level:')
                    else:
                        print('previous_close < current_sr_level:')
                    #  ********************************************************************************************
                    #  LONGS LOGICS BEGIN HERE
                    #  ********************************************************************************************
                    # REJECTION LONGS LOGIC:
                    if previous_close is not None and previous_close > current_sr_level:
                        if current_candle_low < current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Over-Under condition met for long
                                level_interaction_signal = 100
                                level_signal_count[level_column] += 1
                                print(f"Long: 'Under-over' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    potential_ob_time = potential_ob_candle['Time']
                                    print(
                                        f"Looking for RED candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )
                                    # First red candle found
                                    if potential_ob_candle['Close'] < potential_ob_candle['Open']:
                                        print(
                                            f"First RED candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )
                                        # Candle must be above the level
                                        if potential_ob_candle['Close'] > current_sr_level:
                                            red_candle_high = potential_ob_candle['High']
                                            red_candle_found = True
                                            ob_signal = 100
                                            print(
                                                f"It's above the level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(f"But we are not above the level. Checking next candle...")

                                # Step 2: After finding the red candle, wait for the price to hit its high
                                if red_candle_found:
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']
                                        print(
                                            f"Waiting for next candle to close above RED candle high at {next_index},"
                                            f"Time: {signal_time}"
                                        )
                                        # Price hits the high of the red candle
                                        if next_candle_after_ob['Close'] > red_candle_high:
                                            if next_candle_after_ob['Close'] > current_sr_level:
                                                signal = 100  # Long signal
                                                signal_index = next_index
                                                price_level = next_candle_after_ob['Close']

                                                print(
                                                    f"Signal triggered at index {next_index}, "
                                                    f"Time: {signal_time}, "
                                                    f"Candle closing price: {price_level}"
                                                )
                                                break
                                            else:
                                                print(
                                                    f"It closed above, but we are not above the level. "
                                                    f"Checking next candle..."
                                                )
                                        elif next_candle_after_ob['Close'] < next_candle_after_ob['Open']:
                                            signal_time = next_candle_after_ob['Time']
                                            red_candle_high = next_candle_after_ob['High']
                                            stop_price = next_candle_after_ob['Low']
                                            print(
                                                f"NEW RED candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

#                   BR-O LOGIC BEGIN HERE *****************************************************************************
                    # Previous close was below level
                    if previous_close is not None and previous_close < current_sr_level:
                        if current_candle_close > current_sr_level:
                            if current_candle_close > current_sr_level:
                                # Under condition met for long
                                level_interaction_signal = 100
                                level_signal_count[level_column] += 1
                                level_interaction_signal_time = current_candle_time

                                print(f"Long: 'Over' condition met at index {index}, "
                                      f"Time: {current_candle_time}, "
                                      f"SR level: {current_sr_level}")

                                # Step 1: Find the first red candle (where close < open)
                                red_candle_found = False
                                red_candle_high = None

                                for subsequent_index in range(index + 1, len(output_df_with_levels)):

                                    potential_ob_candle = output_df_with_levels.iloc[subsequent_index]
                                    potential_ob_time = potential_ob_candle['Time']

                                    # Calculate the time difference in minutes

                                    print(
                                        f"Looking for RED candle at index {subsequent_index}, "
                                        f"Time: {potential_ob_time}"
                                    )

                                    # First red candle found
                                    if potential_ob_candle['Close'] < potential_ob_candle['Open']:
                                        print(
                                            f"Last RED candle found at index {subsequent_index}, "
                                            f"Time: {potential_ob_time}"
                                        )

                                        if potential_ob_candle['Close'] > current_sr_level:
                                            # Candle must be above the level
                                            red_candle_high = potential_ob_candle['High']
                                            red_candle_found = True
                                            ob_signal = 100
                                            print(
                                                f"It's above the level at index {subsequent_index}, "
                                                f"Time: {potential_ob_time}"
                                            )
                                            break
                                        else:
                                            print(f"But we are not above the level. Checking next candle...")

                                # Step 2: After finding the red candle, wait for the price to hit its high
                                if red_candle_found:
                                    potential_ob_time = pd.to_datetime(potential_ob_time)  # Store the time of the red candle
                                    for next_index in range(subsequent_index + 1, len(output_df_with_levels)):
                                        next_candle_after_ob = output_df_with_levels.iloc[next_index]
                                        signal_time = next_candle_after_ob['Time']

                                        # Calculate the time difference in minutes between the red candle and the current candle
                                        time_diff = (potential_ob_time -
                                                     pd.to_datetime(level_interaction_signal_time)).total_seconds() / 60

                                        print(
                                            f"Waiting for next candle to close above RED candle high at {next_index},"
                                            f"Time: {signal_time}"
                                        )
                                        if time_diff > max_time_waiting_for_entry:
                                            print(
                                                f"Stopping search: "
                                                f"1Exceeded {max_time_waiting_for_entry}-minute window after RED candle at index {next_index}, \n"
                                                f"Level_interaction_signal_time: {level_interaction_signal_time}\n"
                                                f"Red_candle_time: {potential_ob_time}\n"
                                                f"time_diff: {time_diff}"
                                            )
                                            break
                                        if next_candle_after_ob['Close'] > red_candle_high:
                                            # Price hits the high of the red candle
                                            if next_candle_after_ob['Close'] > current_sr_level:
                                                signal = 100  # Long signal
                                                signal_index = next_index
                                                price_level = next_candle_after_ob['Close']

                                                print(
                                                    f"Signal triggered at index {next_index}, "
                                                    f"Time: {signal_time}, "
                                                    f"Candle closing price: {price_level}"
                                                )
                                                break
                                            else:
                                                print(
                                                    f"It closed above, but we are not above the level. "
                                                    f"Checking next candle..."
                                                )
                                        elif next_candle_after_ob['Close'] < next_candle_after_ob['Open']:
                                            next_candle_after_ob_time = pd.to_datetime(next_candle_after_ob['Time'])
                                            signal_time = next_candle_after_ob['Time']
                                            red_candle_high = next_candle_after_ob['High']
                                            stop_price = next_candle_after_ob['Low']
                                            print(
                                                f"NEW RED candle formed at index {next_index}, "
                                                f"Time: {signal_time}, "
                                            )
                                            subsequent_index = next_index
                                            time_diff = (next_candle_after_ob_time -
                                                         pd.to_datetime(
                                                             level_interaction_signal_time)).total_seconds() / 60
                                            if time_diff > max_time_waiting_for_entry:
                                                print(
                                                    f"Stopping search: "
                                                    f"2Exceeded {max_time_waiting_for_entry}-minute window after RED candle at index {next_index}, \n"
                                                    f"Signal_time: {level_interaction_signal_time}\n"
                                                    f"Red_candle_time: {next_candle_after_ob_time}\n"
                                                    f"time_diff: {time_diff}"
                                                )
                                                break
                                    else:
                                        break
                                break  # Exit the level loop once a signal is generated

        # Append values with None for signals not triggered
        rejection_signals_with_prices.append((signal_index, signal, price_level))
        yellow_star_signals_with_prices.append((subsequent_index, ob_signal, stop_price))
        rejection_signals_for_chart.append((signal_index, signal))
        ob_candle_for_chart.append((subsequent_index, ob_signal))
        level_interaction_signal_for_chart.append((index, level_interaction_signal))
    else:
        print(f"Max signals for level {level_column} reached")

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    yellow_star_signals_series_with_prices = pd.Series(yellow_star_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    ob_candle_series_for_chart = pd.Series(ob_candle_for_chart)
    level_interaction_signals_series_for_chart = pd.Series(level_interaction_signal_for_chart)
    return (rejection_signals_series_with_prices,
            yellow_star_signals_series_with_prices,
            rejection_signals_series_for_chart,
            ob_candle_series_for_chart,
            level_interaction_signals_series_for_chart,
            level_signal_count)

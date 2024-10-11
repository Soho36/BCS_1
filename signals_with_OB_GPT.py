import pandas as pd


def level_rejection_signals(df, sr_levels_out):
    rejection_signals_with_prices = []
    rejection_signals_for_chart = []

    df.reset_index(inplace=True)

    for index, row in df.iterrows():
        previous_close = df.iloc[index - 1]['Close'] if index > 0 else None  # Handle first row case
        current_candle_close = row['Close']
        current_candle_high = row['High']
        current_candle_time = row['Time']

        print(f"---\nAnalyzing candle at index {index}, Time: {current_candle_time}, Close: {current_candle_close}, High: {current_candle_high}")

        signal = None  # Reset signal for each row
        price_level = None
        signal_index = None  # Initialize signal_index
        subsequent_index = None     # Initialize subsequent_index

        for level_column in range(1, len(sr_levels_out) + 1):
            current_sr_level = row[level_column]
            if current_sr_level is not None:

                # Check for short signal: over-under condition
                if previous_close is not None and previous_close < current_sr_level:  # Previous close was below level
                    if current_candle_high > current_sr_level and current_candle_close < current_sr_level:
                        # Over-Under condition met
                        print(f"Over-under condition met at index {index}, Time: {current_candle_time}, SR level: {current_sr_level}")

                        # Step 1: Find the first green candle (where close > open)
                        green_candle_found = False
                        green_candle_low = None

                        for subsequent_index in range(index + 1, len(df)):
                            subsequent_row = df.iloc[subsequent_index]
                            subsequent_time = subsequent_row['Time']  # Use the correct time for the subsequent row
                            print(f"Checking subsequent candle at index {subsequent_index}, Time: {subsequent_time}, Close: {subsequent_row['Close']}, Open: {subsequent_row['Open']}")
                            if subsequent_row['Close'] > subsequent_row['Open']:  # First green candle found
                                green_candle_low = subsequent_row['Low']
                                green_candle_found = True
                                print(f"First green candle found at index {subsequent_index}, Time: {subsequent_time}, Low: {green_candle_low}")
                                break  # Exit loop after finding the first green candle

                        # Step 2: After finding the green candle, wait for the price to hit its low
                        if green_candle_found:
                            for next_index in range(subsequent_index + 1, len(df)):
                                next_row = df.iloc[next_index]
                                next_time = next_row['Time']  # Use the correct time for the next row
                                print(f"Checking next candle at index {next_index}, Time: {next_time}, Low: {next_row['Low']}, Target green candle low: {green_candle_low}")
                                if next_row['Low'] <= green_candle_low:  # Price hits the low of the green candle
                                    signal = -100  # Short signal
                                    price_level = green_candle_low  # Enter at the low of the first green candle
                                    signal_index = next_index  # Assign signal_index here
                                    print(f"Signal triggered at index {next_index}, Time: {next_time}, Price level: {price_level}")
                                    break
                        break  # Exit the level loop once a signal is generated

        # Append values with None for signals not triggered
        rejection_signals_with_prices.append((signal_index, signal, price_level))
        rejection_signals_for_chart.append((signal_index, signal))

    # Print signals for verification
    print("\nRejection signals with prices:")
    for signal_index, signal, price_level in rejection_signals_with_prices:
        print(f"Index: {signal_index}, Signal: {signal}, Price Level: {price_level}")

    print("\nRejection signals for chart:")
    for signal_index, signal in rejection_signals_for_chart:
        print(f"Index: {signal_index}, Signal: {signal}")

    rejection_signals_series_with_prices = pd.Series(rejection_signals_with_prices)
    rejection_signals_series_for_chart = pd.Series(rejection_signals_for_chart)
    return rejection_signals_series_with_prices, rejection_signals_series_for_chart

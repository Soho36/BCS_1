import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import statistics
import os

file_path = 'Bars/MESU24_M1_w.csv'
# file_path = 'Bars/MESU24_M2_w.csv'
# file_path = 'Bars/MESU24_M3_w.csv'
# file_path = 'Bars/MESU24_M5_w.csv'
# file_path = 'Bars/MESU24_M15_w.csv'
# file_path = 'Bars/MESU24_M30_w.csv'
# file_path = 'Bars/MESU24_H1_w.csv'
# file_path = 'Bars/MESU24_H2_w.csv'
# file_path = 'Bars/MESU24_H3_w.csv'
# file_path = 'Bars/MESU24_H4_w.csv'
# pd.set_option('display.max_columns', 10)  # Uncomment to display all columns


# **************************************** SETTINGS **************************************

start_date = '2024-07-01'       # Choose the start date to begin from
end_date = '2024-07-02'         # Choose the end date

# SIMULATION
start_simulation = True


# ENTRY CONDITIONS
new_trades_threshold = 5            # Reject new trades placement within this period (min)
use_candle_close_as_entry = False   # Must be False if next condition is True
use_level_price_as_entry = True     # Must be False if previous condition is True
confirmation_close = False          # Candle close above/below level as confirmation
longs_allowed = True                # Allow or disallow trade direction
shorts_allowed = True               # Allow or disallow trade direction

#
use_level_rejection = True
find_levels = True
#


# RISK MANAGEMENT

spread = 0
risk_reward_ratio = 3   # Chose risk/reward ratio (aiming to win compared to lose)
stop_loss_as_candle_min_max = False  # Must be True if next condition is false
stop_loss_offset = 1                 # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

stop_loss_price_as_dollar_amount = True     # STOP as distance from entry price (previous must be false)
rr_dollar_amount = 2                       # Value for stop as distance

stop_loss_as_plus_candle = True
stop_loss_offset_multiplier = 0    # 1 places stop one candle away from H/L (only when stop_loss_as_plus_candle = True


# CHARTS
show_candlestick_chart = True
show_level_rejection_signals = True
show_profits_losses_line_chart = False  # Only when Simulation is True
show_balance_change_line_chart = False   # Only when Simulation is True

# ******************************************************************************


def getting_dataframe_from_file(path):

    print()

    columns_to_parse = ['Date', 'Time', 'Open', 'High', 'Low', 'Close']
    csv_df = pd.read_csv(
        path,
        usecols=columns_to_parse
    )

    print()
    return csv_df


dataframe_from_csv = getting_dataframe_from_file(file_path)
print('Source dataframe: \n', dataframe_from_csv)


def date_range_func(df_csv, start, end):

    # Get the TICKER from the name of the file
    file_name = os.path.basename(file_path)
    ticker = os.path.splitext(file_name)[0]

    # Combine 'Date' and 'Time' into 'DateTime' and convert to datetime
    df_csv['DateTime'] = pd.to_datetime(df_csv['Date'] + ' ' + df_csv['Time'])

    """
    Extend end date to include the whole day
    filtering up to one second before midnight of the next day
    """
    end = pd.to_datetime(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    # Filter by date
    df_filtered_by_date = df_csv[(df_csv['DateTime'] >= start) & (df_csv['DateTime'] <= end)]

    if df_filtered_by_date.empty:
        print('NB! Dataframe is empty, check the date range!')
        exit()  # If dataframe is empty, stop the script

    else:
        return ticker, df_filtered_by_date      # DF MUST BE INDEX RESET


(
    ticker_name,
    filtered_by_date_dataframe
) = date_range_func(
    dataframe_from_csv,
    start_date,
    end_date
)

print('Filtered dataframe: \n', filtered_by_date_dataframe)

"""
In order to draw levels we need to resample M1 datapoints to H1
"""
def resample_m1_datapoints(df_filtered_by_date):
    df_filtered_by_date.set_index('DateTime', inplace=True)     # Set index to DateTime for .agg function
    df_h1 = df_filtered_by_date.resample('H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })
    df_h1_cleaned = df_h1.dropna()              # Remove NaN rows from the Dataframe
    return df_h1_cleaned


aggregated_filtered_df = resample_m1_datapoints(filtered_by_date_dataframe)

print('Aggregated dataframe: \n', aggregated_filtered_df)


filtered_by_date_dataframe_original = filtered_by_date_dataframe.copy()     # Passed to Simulation
print('Copy of original: \n', filtered_by_date_dataframe_original)


print()
# print(f'Dataframe filtered by date:\n {filtered_by_date_dataframe}')
print()
print('************************************ TRADES SIMULATION ************************************')

#  ----------------------------------------------------------------------------------------------
#  SEARCH FOR PRICE LEVELS
#  ----------------------------------------------------------------------------------------------


filtered_by_date_dataframe = filtered_by_date_dataframe.loc[:, ['Open', 'High', 'Low', 'Close']]


if find_levels:
    def levels_discovery(agg_filtered_df):
        print('levels_discovery DF: \n', agg_filtered_df)

        levels_startpoints_tuples = []
        levels_endpoints_tuples = []

        level_discovery_signal = []
        level_discovery_signal.insert(0, None)
        level_discovery_signal.insert(1, None)

        support_levels = []
        resistance_levels = []
        sr_levels = []
        sr_levels_with_datetime = []

        # Support levels
        for i in range(2, len(agg_filtered_df) - 2):
            if (agg_filtered_df['Low'][i] < agg_filtered_df['Low'][i - 1]) and \
               (agg_filtered_df['Low'][i] < agg_filtered_df['Low'][i + 1]) and \
               (agg_filtered_df['Low'][i + 1] < agg_filtered_df['Low'][i + 2]) and \
               (agg_filtered_df['Low'][i - 1] < agg_filtered_df['Low'][i - 2]):
                datetime_1 = agg_filtered_df.index[i]
                price_level_1 = agg_filtered_df['Low'][i]
                datetime_2 = agg_filtered_df.index[-1]
                price_level_2 = agg_filtered_df['Low'][i]

                if not is_near_level(
                        price_level_1,
                        levels_startpoints_tuples,
                        agg_filtered_df
                ):
                    levels_startpoints_tuples.append((datetime_1, price_level_1))
                    levels_endpoints_tuples.append((datetime_2, price_level_2))
                    support_levels.append(price_level_1)
                    level_discovery_signal.append(0)
                    sr_levels.append((i, price_level_1))  # SR levels
                    sr_levels_with_datetime.append((datetime_1, price_level_1))

                else:
                    level_discovery_signal.append(None)

            # Resistance levels
            elif ((agg_filtered_df['High'][i] > agg_filtered_df['High'][i - 1]) and
                  (agg_filtered_df['High'][i] > agg_filtered_df['High'][i + 1]) and
                  (agg_filtered_df['High'][i + 1] > agg_filtered_df['High'][i + 2]) and
                  (agg_filtered_df['High'][i - 1] > agg_filtered_df['High'][i - 2])):
                datetime_1 = agg_filtered_df.index[i]
                price_level_1 = agg_filtered_df['High'][i]
                datetime_2 = agg_filtered_df.index[-1]
                price_level_2 = agg_filtered_df['High'][i]

                if not is_near_level(
                        price_level_1,
                        levels_startpoints_tuples,
                        agg_filtered_df
                ):
                    levels_startpoints_tuples.append((datetime_1, price_level_1))
                    levels_endpoints_tuples.append((datetime_2, price_level_2))
                    resistance_levels.append(price_level_1)
                    level_discovery_signal.append(0)
                    sr_levels.append((i, price_level_1))  # SR levels
                else:
                    level_discovery_signal.append(None)

            else:
                level_discovery_signal.append(None)

        level_discovery_signal.extend([None, None])  # Appending two elements to the end, to match Dataframe length

        level_discovery_signals_series = pd.Series(level_discovery_signal)

        print('levels_startpoints_tuples', levels_startpoints_tuples)
        print('levels_endpoints_tuples', levels_endpoints_tuples)
        print('support_levels', support_levels)
        print('resistance_levels', resistance_levels)
        print('level_discovery_signals_series', level_discovery_signals_series)
        print('sr_levels', sr_levels)
        return (
            levels_startpoints_tuples,
            levels_endpoints_tuples,
            support_levels,
            resistance_levels,
            level_discovery_signals_series,
            sr_levels
        )


    def is_near_level(value, levels, df):
        average = np.mean(df['High'] - df['Low'])
        return any(abs(value - level) < average for _, level in levels)


    (
        levels_startpoints_to_chart,
        levels_endpoints_to_chart,
        support_level_signal_running_out,
        resistance_level_signal_running_out,
        level_discovery_signals_series_out,
        sr_levels_out
    ) = levels_discovery(aggregated_filtered_df)

    levels_points_for_chart = [[a, b] for a, b in zip(levels_startpoints_to_chart, levels_endpoints_to_chart)]

else:
    sr_levels_out = []                          # Initialize sr_levels_out with an empty list to avoid warning
    level_discovery_signals_series_out = []     # Initialize sr_levels_out with an empty list to avoid warning
    levels_startpoints_to_chart = []


# ********************************************************************************************************************
filtered_by_date_dataframe.reset_index(inplace=True)
print('SR_levels_out: \n', sr_levels_out)
print('levels_startpoints: \n', levels_startpoints_to_chart)


def add_columns_and_levels_to_dataframe(df):
    print('add_columns_and_levels_: \n', df)
    df.set_index('DateTime', inplace=True)

    """
    Count how many columns are needed to add levels values to dataframe.
    Return dictionary like {1: 1, 2: 1, 3: 1, 4: 1}
    Insert new columns to Dataframe
    Update corresponding row with price level
    """
    n = 1
    column_counters = {}
    while n < (len(levels_startpoints_to_chart) + 1):
        column_counters[n] = 0
        n += 1
    # print(column_counters)

    # Loop through the price levels
    for datetime, price in levels_startpoints_to_chart:
        # Determine which column to assign the price level to
        column_number = min(column_counters, key=column_counters.get)
        # Update that column of dataframe with the price level
        df.loc[datetime, column_number] = price
        # Increment the counter for the assigned column
        column_counters[column_number] += 1

    return column_counters


column_counters_outside = add_columns_and_levels_to_dataframe(filtered_by_date_dataframe)
print('column_counters_outside: ', column_counters_outside)

filtered_by_date_dataframe.reset_index(inplace=True)


def fill_column_with_first_non_null_value(df, column_idx):
    print('fill_column_with_first_non_null_value: \n', df.iloc[0:50])
    """
    Fill the columns down till the end with level price after first not null value discovered
    Example:
                             Open     High      Low  ...        6       7       8
    Datetime                                        ...
    2024-06-17 00:00:00  5502.00  5503.25  5500.25  ...      NaN     NaN     NaN
    2024-06-17 01:00:00  5500.75  5501.00  5497.25  ...      NaN     NaN     NaN
    2024-06-17 02:00:00  5500.00  5501.75  5498.50  ...      NaN     NaN     NaN
    2024-06-17 03:00:00  5499.50  5501.75  5499.25  ...      NaN     NaN     NaN
    2024-06-17 04:00:00  5500.50  5502.00  5498.50  ...      NaN     NaN     NaN
    ...                      ...      ...      ...  ...      ...     ...     ...
    2024-07-03 14:00:00  5563.75  5572.50  5542.25  ...  5510.25  NaN        NaN
    2024-07-03 15:00:00  5575.75  5582.50  5572.25  ...  5510.25  5552.0     NaN
    2024-07-03 16:00:00  5581.25  5595.50  5580.50  ...  5510.25  5552.0  5595.5
    2024-07-03 17:00:00  5590.75  5592.50  5589.00  ...  5510.25  5552.0  5595.5
    2024-07-03 22:00:00  5590.50  5591.50  5586.25  ...  5510.25  5552.0  5595.5
    """

    # Check if any non-null value exists in the column
    if not df[column_idx].isna().all():
        # Get the first non-null value
        value_to_fill = df[column_idx].dropna().iloc[0]

        # Find the index of the first occurrence of the non-null value
        start_index = df.loc[df[column_idx] == value_to_fill].index[0]

        # Iterate through the DataFrame and fill the values with the non-null value
        for idx, val in df.iterrows():
            if idx >= start_index:
                df.loc[idx, column_idx] = value_to_fill


# Fill each column with the first non-null value
for column_index in range(1, len(column_counters_outside) + 1):
    fill_column_with_first_non_null_value(filtered_by_date_dataframe, column_index)

filtered_by_date_dataframe.set_index('DateTime', inplace=True)  # Contains levels columns
print('Dataframe with level columns: \n', filtered_by_date_dataframe.iloc[0:50])

# *******************************************************************************************************************
#  ----------------------------------------------------------------------------------------------
#  LEVEL REJECTION SIGNALS
#  ----------------------------------------------------------------------------------------------


if find_levels and use_level_rejection:

    def level_rejection_signals(df):
        # print('level_rejection_signals DF \n', df)

        rejection_signals_with_prices = []
        rejection_signals_for_chart = []

        df.reset_index(inplace=True)
        print('DATAFRAME INSIDE level_rejection_signals(df): \n', df.iloc[0:50])

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
                    if previous_close < current_sr_level:   # Check if the previous close was below the resistance level
                        if current_candle_high > current_sr_level:    # Price has crossed above resistance level
                            if use_level_price_as_entry:
                                signal = -100
                                price_level = current_sr_level
                                break
                            elif use_candle_close_as_entry:
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


    (rejection_signals_series_outside,
     rejection_signals_series_for_chart_outside) = (
        level_rejection_signals(filtered_by_date_dataframe)
    )

    print('Rejection_signals_series: \n', rejection_signals_series_outside)
    # print('Level_discovery_signals: \n', level_discovery_signals_series_out)
    filtered_by_date_dataframe.set_index('DateTime', inplace=True)  # Set index back to Datetime
else:
    rejection_signals_series_outside = None  # When function switched off
    rejection_signals_series_for_chart_outside = None


#  ----------------------------------------------
#  TRADES SIMULATION
#  ----------------------------------------------


def trades_simulation(
        filtered_df_original,
        risk_reward_simulation,
        sl_offset_multiplier
):
    # print('!!!!', filtered_df_original)

    #   Convert Date column to Datetime object
    filtered_df_original['Date'] = pd.to_datetime(filtered_df_original['Date'])
    filtered_df_original.reset_index(inplace=True)
    if start_simulation:
        trades_counter = 0
        trade_result_both = []
        trade_result = []
        trade_result_longs = []
        trade_result_shorts = []
        trade_direction = []
        profit_loss_long_short = []     # List of profits and losses by longs and shorts

        if use_level_rejection:

            signal_series = rejection_signals_series_outside
            for signal_index, (signal_value, price_level) in enumerate(signal_series):

                # LONG TRADES LOGIC
                if signal_value == 100 and longs_allowed:
                    # Check the previous 5 signals to avoid open new trades too close to each other
                    previous_signals = signal_series[max(0, signal_index - new_trades_threshold):signal_index]

                    if any(prev_signal in (100, -100) for prev_signal, _ in previous_signals):
                        # If there is any signal with value 100 or -100 in the previous 5 signals, skip this signal
                        print(f"Skipping signal at index {signal_index} due to new trades threshold")
                        continue

                    trades_counter += 1
                    trade_direction.append('Long')
                    signal_candle_date = (filtered_df_original.iloc[signal_index]['Date']).strftime('%Y-%m-%d')
                    signal_candle_time = filtered_df_original.iloc[signal_index]['Time']
                    signal_candle_low = round(filtered_df_original.iloc[signal_index]['Low'], 3)

                    if use_level_price_as_entry:
                        entry_price = price_level

                    elif use_candle_close_as_entry:
                        entry_price = round(filtered_df_original.iloc[signal_index]['Close'], 3)   # ENTRY

                    else:
                        entry_price = None
                        print("Choose entry type".upper())

                    stop_loss_price = None
                    take_profit_price = None

                    if stop_loss_as_candle_min_max:  # STOP as candle low
                        stop_loss_price = (signal_candle_low - stop_loss_offset)
                        take_profit_price = (
                                (((entry_price - stop_loss_price) * risk_reward_simulation)
                                 + entry_price) + stop_loss_offset
                        )

                    elif stop_loss_price_as_dollar_amount:  # STOP as distance from entry price
                        stop_loss_price = entry_price - rr_dollar_amount
                        take_profit_price = entry_price + (rr_dollar_amount * risk_reward_ratio)

                    elif stop_loss_as_plus_candle:
                        stop_loss_price = (signal_candle_low - ((entry_price - signal_candle_low)
                                                                * sl_offset_multiplier))
                        take_profit_price = (((entry_price - stop_loss_price) * risk_reward_simulation) +
                                             entry_price)
                    else:
                        print('Stop loss condition is not properly defined')

                    print('------------------------------------------------------------------------------------------')
                    print(f'▲ ▲ ▲ OPEN LONG TRADE: ▲ ▲ ▲ {signal_candle_date} {signal_candle_time}')
                    print(f'Entry price: {entry_price}')
                    print(f'Take: {round(take_profit_price, 3)} ({risk_reward_simulation}RR)')
                    print(f'Stop: {stop_loss_price}')

                    print()

                    for j in range(signal_index, len(filtered_df_original)):
                        current_candle_date = (filtered_df_original.iloc[j]['Date']).strftime('%Y-%m-%d')
                        current_candle_time = (filtered_df_original.iloc[j]['Time'])
                        current_candle_open = filtered_df_original.iloc[j]['Open']
                        current_candle_high = filtered_df_original.iloc[j]['High']
                        current_candle_low = filtered_df_original.iloc[j]['Low']
                        current_candle_close = filtered_df_original.iloc[j]['Close']

                        print('Next candle: ', current_candle_date, current_candle_time, '|',
                              'O', current_candle_open,
                              'H', current_candle_high,
                              'L', current_candle_low,
                              'C', current_candle_close)

                        if current_candle_low <= stop_loss_price and current_candle_high >= take_profit_price:
                            trade_result_both.append(1)
                            print('BOTH')

                        if current_candle_low <= stop_loss_price:
                            trade_result.append((stop_loss_price - spread) -
                                                (entry_price + spread))
                            trade_result_longs.append((stop_loss_price - spread) -
                                                      (entry_price + spread))
                            profit_loss_long_short.append('LongLoss')
                            print(f'□ □ □ Stop Loss hit □ □ □ at {current_candle_date} {current_candle_time}')
                            print()
                            print(f'Trade Close Price: {round(stop_loss_price, 3)}')

                            print(
                              f'P/L: ${round((stop_loss_price - spread) - (entry_price + spread), 3)}'
                            )
                            print(
                                '---------------------------------------------'
                                '---------------------------------------------'
                            )
                            break

                        elif current_candle_high >= take_profit_price:
                            trade_result.append(take_profit_price - (entry_price + spread))
                            trade_result_longs.append(take_profit_price - (entry_price + spread))
                            profit_loss_long_short.append('LongProfit')
                            print(f'○ ○ ○ Take profit hit ○ ○ ○ at {current_candle_date} {current_candle_time}')
                            print()
                            print(f'Trade Trade Close Price: {round(take_profit_price, 3)}')

                            print(f'P/L: ${round(take_profit_price - (entry_price + spread), 3)}')
                            print(
                                '---------------------------------------------'
                                '---------------------------------------------'
                            )
                            break

                        else:
                            pass

                # SHORT TRADES LOGIC
                elif signal_value == -100 and shorts_allowed:
                    # Check the previous 5 signals to avoid open new trades too close to each other
                    previous_signals = signal_series[max(0, signal_index - new_trades_threshold):signal_index]

                    if any(prev_signal in (100, -100) for prev_signal, _ in previous_signals):
                        # If there is any signal with value 100 or -100 in the previous 5 signals, skip this signal
                        print(f"Skipping signal at index {signal_index} due to new trades threshold")
                        continue

                    trades_counter += 1
                    trade_direction.append('Short')
                    signal_candle_date = (filtered_df_original.iloc[signal_index]['Date']).strftime('%Y-%m-%d')
                    signal_candle_time = filtered_df_original.iloc[signal_index]['Time']
                    signal_candle_high = round(filtered_df_original.iloc[signal_index]['High'], 3)

                    if use_level_price_as_entry:
                        entry_price = price_level

                    elif use_candle_close_as_entry:
                        entry_price = round(filtered_df_original.iloc[signal_index]['Close'], 3)   # ENTRY

                    else:
                        entry_price = None
                        print("Choose entry type".upper())

                    stop_loss_price = None
                    take_profit_price = None

                    if stop_loss_as_candle_min_max:
                        stop_loss_price = signal_candle_high + stop_loss_offset
                        take_profit_price = ((entry_price -
                                              ((stop_loss_price - entry_price)
                                               * risk_reward_simulation))) - stop_loss_offset

                    elif stop_loss_price_as_dollar_amount:  # STOP as distance from entry price
                        stop_loss_price = entry_price + rr_dollar_amount
                        take_profit_price = entry_price - (rr_dollar_amount * risk_reward_ratio)

                    elif stop_loss_as_plus_candle:
                        # Adding size of the signal candle to the stop
                        stop_loss_price = (signal_candle_high +
                                           ((signal_candle_high - entry_price)
                                            * sl_offset_multiplier))
                        take_profit_price = (entry_price -
                                             ((stop_loss_price - entry_price) * risk_reward_simulation))
                    else:
                        print('Stop loss condition is not properly defined')

                    print('------------------------------------------------------------------------------------------')
                    print(f'▼ ▼ ▼ OPEN SHORT TRADE: ▼ ▼ ▼ {signal_candle_date} {signal_candle_time}')
                    print(f'Entry price: {entry_price}')
                    print(f'Stop: {stop_loss_price}')
                    print(f'Take: {round(take_profit_price, 3)} ({risk_reward_simulation}RR)')

                    print()

                    for j in range(signal_index, len(filtered_df_original)):
                        current_candle_date = (filtered_df_original.iloc[j]['Date']).strftime('%Y-%m-%d')
                        current_candle_time = (filtered_df_original.iloc[j]['Time'])
                        current_candle_open = filtered_df_original.iloc[j]['Open']
                        current_candle_high = filtered_df_original.iloc[j]['High']
                        current_candle_low = filtered_df_original.iloc[j]['Low']
                        current_candle_close = filtered_df_original.iloc[j]['Close']

                        print('Next candle: ', current_candle_date, current_candle_time, '|',
                              'O', current_candle_open,
                              'H', current_candle_high,
                              'L', current_candle_low,
                              'C', current_candle_close)

                        if current_candle_high >= stop_loss_price and current_candle_low <= take_profit_price:
                            trade_result_both.append(1)
                            print('BOTH')

                        if current_candle_high >= stop_loss_price:
                            trade_result.append((entry_price - spread) -
                                                (stop_loss_price + spread))
                            trade_result_shorts.append((entry_price - spread) -
                                                       (stop_loss_price + spread))
                            profit_loss_long_short.append('ShortLoss')
                            print(f'□ □ □ Stop Loss hit □ □ □ at {current_candle_date} {current_candle_time}')
                            print()
                            print(f'Trade Close Price: {round(stop_loss_price, 3)}')

                            print(
                              f'P/L: ${round((entry_price - spread) - (stop_loss_price + spread), 3)}'
                            )
                            print(
                                '---------------------------------------------'
                                '---------------------------------------------'
                            )
                            break

                        elif current_candle_low <= take_profit_price:
                            trade_result.append((entry_price - spread) - take_profit_price)
                            trade_result_shorts.append((entry_price - spread) - take_profit_price)
                            profit_loss_long_short.append('ShortProfit')
                            print(f'○ ○ ○ Take profit hit ○ ○ ○ at {current_candle_date} {current_candle_time}')
                            print()
                            print(f'Trade Close Price: {round(take_profit_price, 3)}')

                            print(f'P/L: ${round((entry_price - spread) - take_profit_price, 3)}')
                            print(
                                '---------------------------------------------'
                                '---------------------------------------------'
                            )

                            break

                        else:
                            pass

            return (
                trade_result_both,
                trade_result,
                trades_counter,
                trade_direction,
                profit_loss_long_short,
                trade_result_longs,
                trade_result_shorts
            )
    else:
        print('Trade simulation is OFF')
        return None, None, None, None, None, None, None   # Return Nones in order to avoid error when function is OFF


(
    trade_result_both_to_trade_analysis,
    trade_results_to_trade_analysis,
    trades_counter_to_trade_analysis,
    trade_direction_to_trade_analysis,
    profit_loss_long_short_to_trade_analysis,
    trade_result_longs_to_trade_analysis,
    trade_result_shorts_to_trade_analysis
) = trades_simulation(
    filtered_by_date_dataframe_original,
    risk_reward_ratio,
    stop_loss_offset_multiplier
)


def trades_analysis(
        trade_result_both,
        trade_result,
        trades_counter,
        trade_direction,
        profit_loss_long_short,
        trade_result_longs,
        trade_result_short,
        df_csv
):

    if start_simulation and use_level_rejection:

        first_row = df_csv.iloc[0]['Date']
        last_row = df_csv.iloc[-1]['Date']
        print()
        print('*****************************************************************************************')
        print('-------------------------------------TRADES ANALYSIS-------------------------------------')
        print('*****************************************************************************************')
        print(f'Ticker: {ticker_name}')
        print()
        print(f'Selected Date range: {start_date} - {end_date}'.upper(),
              f'(available period: {first_row}-{last_row})'.title()
              )
        print()

        if trades_counter == 0:
            print("No trades were placed! Try other pattern or broader date range")

        rounded_trades_list = 0
        try:
            rounded_trades_list = [round(num, 3) for num in trade_result]   # List of all trades in dollar amount
            # print(f"Trades List: {rounded_trades_list}")
        except TypeError:
            print(f'Trades List: {rounded_trades_list}')

        outcomes_string = []     # List of trade outcomes: profit or loss in order to calculate profitability %
        outcomes_positive = []      # List of positive trades

        outcomes_negative = []      # List of negative trades

        try:
            for num in rounded_trades_list:
                if num > 0:
                    outcomes_string.append('profit')
                    outcomes_positive.append(num)
                else:
                    outcomes_string.append('loss')
                    outcomes_negative.append(num)
            # print(f'Profitable trades list: {outcomes_positive}')
            # print(f'Losing trades list: {outcomes_negative}')
        except TypeError:
            print('Profitable trades list: No trades')
            print('Losing trades list: No trades')
        # Accumulate the sum of consecutive elements to illustrate balance change over time
        results_as_balance_change = []

        running_sum = 0
        try:
            running_sum = rounded_trades_list[0]
        except IndexError:
            pass

        for num in rounded_trades_list[1:]:
            running_sum += num
            results_as_balance_change.append(running_sum)

        rounded_results_as_balance_change = [round(x, 3) for x in results_as_balance_change]
        trades_count = len(outcomes_string)  # Total trades number
        profitable_trades_count = outcomes_string.count('profit')    # Profitable trades number
        losing_trades_count = outcomes_string.count('loss')    # Losing trades number

        win_percent = 0
        try:
            win_percent = (profitable_trades_count * 100) / trades_count    # Profitable trades %
        except ZeroDivisionError:
            pass

        loss_percent = 0
        try:
            loss_percent = (losing_trades_count * 100) / trades_count     # Losing trades %
        except ZeroDivisionError:
            pass
        candles_number_analyzed = len(filtered_by_date_dataframe)      # Total candles in analysis
        trades_per_candle = round(trades_count / candles_number_analyzed, 2)  # How many trades are placed in one day
        days_per_trade = 0
        try:
            days_per_trade = round(1 / trades_per_candle)      # 1 trade is placed in how many days
        except ZeroDivisionError:
            pass
        count_longs = trade_direction.count('Long')
        count_shorts = trade_direction.count('Short')
        try:
            count_profitable_longs_percent = round((profit_loss_long_short.count('LongProfit') * 100) /
                                                   count_longs, 2)
        except ZeroDivisionError:
            count_profitable_longs_percent = 0
            # print("No long trades were made")
        try:
            count_profitable_shorts_percent = round((profit_loss_long_short.count('ShortProfit') * 100) /
                                                    count_shorts, 2)
        except ZeroDivisionError:
            count_profitable_shorts_percent = 0
            # print("No short trades were made")

        # print(f'{profit_loss_long_short}')
        # print(f'List {trade_direction}')
        # print(f'Balance change over time list: {rounded_results_as_balance_change}')
        print()
        print(f'Spread: ${spread}')
        print(f'Total candles in range: {candles_number_analyzed}'.title())
        if days_per_trade > 0:
            print(f'Trades per candle: {trades_per_candle} or 1 trade every {days_per_trade} candles'.title())
        else:
            print('Trades per day: 0')
        print(f'Trades count: {trades_counter}'.title())
        print(f'Closed trades: {trades_count}'.title())
        print('**************************')
        print(f'*  risk_reward_ratio: {risk_reward_ratio}  *')
        print('**************************')
        print()
        print(f'Both trades: {sum(trade_result_both)}')
        print(f'Profitable trades: {profitable_trades_count} ({round(win_percent, 2)}%)'.title())
        print(f'Losing trades: {losing_trades_count} ({round(loss_percent, 2)}%)'.title())
        print()
        print(f'Long trades: {count_longs} ({count_profitable_longs_percent}% profitable out of all longs) '
              f'P/L: ${round(sum(trade_result_longs), 2)}'.title())
        print(f'Short trades: {count_shorts} ({count_profitable_shorts_percent}% profitable out of all shorts) '
              f'P/L: ${round(sum(trade_result_short), 2)}'.title())
        print()

        try:
            print(f'Best trade: ${max(rounded_trades_list)}'.title())
        except ValueError:
            print('Best trade: $0')

        try:
            print(f'Worst trade: ${min(rounded_trades_list)}'.title())
        except ValueError:
            print('Worst trade: $0')

        print()

        if len(outcomes_positive) > 0:
            print(f'Average profitable trade: ${round(statistics.mean(outcomes_positive), 2)}')
        else:
            print(f'Average profitable trade: No profitable trades')

        if len(outcomes_negative) > 0:
            print(f'Average losing trade: ${round(statistics.mean(outcomes_negative), 2)}')
        else:
            print(f'Average losing trade: No losing trades')

        print()
        # Calculating mathematical expectation

        # try:
        #     prob_per_trade = 1 / trades_count
        # except ZeroDivisionError:
        #     print('No closed trades')
        #
        # math_expectation = round(sum([outcome * prob_per_trade for outcome in trade_result]), 2)
        #
        # print(f'Expectation: ${math_expectation}')
        print()

        spread_loss = -1 * ((losing_trades_count * (spread * 2)) + (profitable_trades_count * spread))
        pending_order_spread_loss = -1 * (losing_trades_count * spread)

        print(f'Spread loss: ${spread_loss}'.title())
        print(f'If Pending Order spread loss : ${pending_order_spread_loss}'.title())
        print()

        p_n_l = round(sum(trade_result), 2)

        print(f'If not spread profit/loss: ${round(p_n_l - spread_loss, 2)}'.title())
        print(f'If pending order dollar per share profit/loss: ${p_n_l - pending_order_spread_loss}'.title())
        print('***************************************************************************************')
        print(f'*                       Dollar per Share profit/loss: ${p_n_l}                        *'.title())
        print('***************************************************************************************')

        return rounded_trades_list, rounded_results_as_balance_change

    else:
        print()
        return None, None    # Return Nones in order to avoid error when function is OFF


(
    rounded_trades_list_to_chart_profits_losses,
    rounded_results_as_balance_change_to_chart_profits
) = trades_analysis(
    trade_result_both_to_trade_analysis,
    trade_results_to_trade_analysis,
    trades_counter_to_trade_analysis,
    trade_direction_to_trade_analysis,
    profit_loss_long_short_to_trade_analysis,
    trade_result_longs_to_trade_analysis,
    trade_result_shorts_to_trade_analysis,
    dataframe_from_csv)

#  ----------------------------------------------
#  PLOT CHART
#  ----------------------------------------------


# BALANCE CHANGE CHART
def plot_line_chart_balance_change(rounded_results_as_balance_change):

    if show_balance_change_line_chart and start_simulation:
        plt.figure(figsize=(10, 6))
        try:
            plt.plot(rounded_results_as_balance_change)
        except ValueError:
            print('No balance change chart to print (Trade analysis is OFF)\n')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title(f'Balance change over specified {start_date} - {end_date} date range ({ticker_name})')
        plt.grid(axis='y')


plot_line_chart_balance_change(rounded_results_as_balance_change_to_chart_profits)


# P/L LINE CHART
def plot_line_chart_profits_losses(rounded_trades_list):

    if show_profits_losses_line_chart and start_simulation:
        plt.figure(figsize=(10, 6))
        plt.plot(rounded_trades_list)
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Trades over specified date range')
        plt.grid(axis='y')


plot_line_chart_profits_losses(rounded_trades_list_to_chart_profits_losses)


#  ----------------------------------------------
#  HIGHLIGHT SIGNALS
#  ----------------------------------------------


#  CANDLESTICK CHART
def plot_candlestick_chart(
        df,
        level_discovery_signals_series,
        rejection_signals_series
):
    print('CHART DF: \n', df)
    print('CHART level_discovery_signals_series: \n', level_discovery_signals_series)
    print('CHART rejection_signals_series: \n', rejection_signals_series)

    if show_candlestick_chart:

        # df.set_index('Datetime', inplace=True)
        plots_list = []

        # for i, s in enumerate(level_discovery_signals_series):
        #     if s != 'NaN':
        #         plots_list.append(
        #             mpf.make_addplot(
        #                 level_discovery_signals_series,
        #                 type='scatter',
        #                 color='black',
        #                 markersize=250,
        #                 marker='*',
        #                 panel=1
        #             )
        #         )

        for i, s in enumerate(rejection_signals_series):
            if s != 'NaN':
                plots_list.append(
                    mpf.make_addplot(
                        rejection_signals_series,
                        type='scatter',
                        color='black',
                        markersize=250,
                        marker='+',
                        panel=1))

        print()

        if find_levels:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                alines=dict(alines=levels_points_for_chart, linewidths=2, alpha=0.4),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list
            )

        else:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list
            )


try:
    plot_candlestick_chart(
        filtered_by_date_dataframe,
        level_discovery_signals_series_out,
        rejection_signals_series_for_chart_outside
    )

except KeyboardInterrupt:
    print('Program stopped manually')

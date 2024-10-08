import pandas as pd
# import numpy as np


def levels_discovery(agg_filtered_df):
    # Manually define the support and resistance levels (index or datetime and price level)
    # Format: [(index_or_datetime, price_level)]
    hardcoded_support_levels = [('2024-09-23 10:00:00', 5783.60)]  # Example support levels
    hardcoded_resistance_levels = [('2024-09-23 10:00:00', 5750.00)]  # Example resistance levels

    hardcoded_support_levels = [(pd.Timestamp(date_str), price) for date_str, price in hardcoded_support_levels]
    hardcoded_resistance_levels = [(pd.Timestamp(date_str), price) for date_str, price in hardcoded_resistance_levels]

    levels_startpoints_tuples = []
    levels_endpoints_tuples = []
    support_levels = []
    resistance_levels = []
    sr_levels = []  # Support/Resistance levels with index
    sr_levels_with_datetime = []  # Support/Resistance levels with datetime

    # Support levels
    for datetime_1, price_level_1 in hardcoded_support_levels:
        datetime_2 = agg_filtered_df.index[-1]  # Use the last datetime for endpoint
        levels_startpoints_tuples.append((datetime_1, price_level_1))
        levels_endpoints_tuples.append((datetime_2, price_level_1))
        support_levels.append(price_level_1)
        sr_levels.append((datetime_1, price_level_1))  # Store with index
        sr_levels_with_datetime.append((datetime_1, price_level_1))

    # Resistance levels
    for datetime_1, price_level_1 in hardcoded_resistance_levels:
        datetime_2 = agg_filtered_df.index[-1]  # Use the last datetime for endpoint
        levels_startpoints_tuples.append((datetime_1, price_level_1))
        levels_endpoints_tuples.append((datetime_2, price_level_1))
        resistance_levels.append(price_level_1)
        sr_levels.append((datetime_1, price_level_1))  # Store with index
        sr_levels_with_datetime.append((datetime_1, price_level_1))

    # Fill signals list with None as we are not generating discovery signals
    level_discovery_signal = [None] * len(agg_filtered_df)

    return (
        levels_startpoints_tuples,
        levels_endpoints_tuples,
        support_levels,
        resistance_levels,
        pd.Series(level_discovery_signal),  # No discovery signals, just fill with None
        sr_levels  # The SR levels list with manually added levels
    )


def add_columns_and_levels_to_dataframe(df, levels_startpoints_to_chart):
    print(df.columns)
    print('5. add_columns_and_levels_: \n', df)
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


def fill_column_with_first_non_null_value(df, column_idx):
    print(df.columns)
    print('6. fill_column_with_first_non_null_value: \n', df)   # .iloc[0:50]

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


# filtered_by_date_dataframe.set_index('DateTime', inplace=True)  # Contains levels columns
# The rest of the process_levels function remains unchanged
def process_levels(filtered_by_date_dataframe, aggregated_filtered_df):
    # Step 1: Discover levels
    (
        levels_startpoints_to_chart,
        levels_endpoints_to_chart,
        support_level_signal_running_out,
        resistance_level_signal_running_out,
        level_discovery_signals_series_out,
        sr_levels_out
    ) = (levels_discovery(aggregated_filtered_df))

    print('SR_levels_out: \n', sr_levels_out)
    print('levels_startpoints: \n', levels_startpoints_to_chart)

    # Step 2: Add columns and levels to dataframe
    filtered_by_date_dataframe = filtered_by_date_dataframe.copy()
    column_counters = add_columns_and_levels_to_dataframe(filtered_by_date_dataframe, levels_startpoints_to_chart)
    print('column_counters_outside: ', column_counters)

    # Step 3: Fill columns with the first non-null value
    for column_index in range(1, len(column_counters) + 1):
        fill_column_with_first_non_null_value(filtered_by_date_dataframe, column_index)
        print('7. Dataframe with level columns: \n', filtered_by_date_dataframe)    # .iloc[0:50]
    output_df_with_levels = filtered_by_date_dataframe.copy()

    return (levels_startpoints_to_chart,
            levels_endpoints_to_chart,
            support_level_signal_running_out,
            resistance_level_signal_running_out,
            level_discovery_signals_series_out,
            sr_levels_out,
            aggregated_filtered_df,
            output_df_with_levels)

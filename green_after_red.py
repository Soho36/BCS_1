import pandas as pd

start_date = '2024-11-22 14:30'  # Choose the start date to begin from
end_date = '2024-11-22 21:00'  # Choose the end date

file_path = 'Bars/1430w.csv'

pd.set_option('display.max_rows', 100)  # Increase the number of rows shown
pd.set_option('display.max_columns', 8)  # Increase the number of columns shown
pd.set_option('display.width', 500)  # Increase the terminal width for better visibility


def getting_dataframe_from_file(path):

    print()

    columns_to_parse = ['Date', 'Time', 'Open', 'High', 'Low', 'Close']
    csv_df = pd.read_csv(
        path,
        usecols=columns_to_parse
    )

    print()
    print('1. Source dataframe: \n', csv_df)
    return csv_df


dataframe_csv = getting_dataframe_from_file(file_path)


def date_range_func(df_csv, start, end):

    # Convert start and end directly to datetime
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # Combine 'Date' and 'Time' into 'DateTime' and convert to datetime
    df_csv['DateTime'] = pd.to_datetime(df_csv['Date'] + ' ' + df_csv['Time'])

    # Filter by date
    df_filtered_by_date = df_csv[(df_csv['DateTime'] >= start) & (df_csv['DateTime'] <= end)]
    df_filtered_by_date = df_filtered_by_date.copy()
    # print('!!!', df_filtered_by_date)
    if df_filtered_by_date.empty:
        print('NB! Dataframe is empty, check the date range!')
        exit()  # If dataframe is empty, stop the script

    else:
        print('2. Filtered dataframe: \n', df_filtered_by_date)
        return df_filtered_by_date      # DF MUST BE INDEX RESET


ranged_df = date_range_func(dataframe_csv, start_date, end_date)
# print(ranged_df[:50])

# Determine candle color
ranged_df['Current_Candle_color'] = ranged_df.apply(lambda row: 'G' if row['Close'] > row['Open'] else 'R', axis=1)
print("All candle colors:\n", ranged_df[:25])
# Calculate candle body sizes
ranged_df['Current_Body_Size'] = abs(ranged_df['High'] - ranged_df['Low'])
# Identify sequences of two consecutive candles
ranged_df['Prev_Candle_color'] = ranged_df['Current_Candle_color'].shift(1)
print("Prev_Candle:\n", ranged_df[:25])
ranged_df['Prev_Body_Size'] = ranged_df['Current_Body_Size'].shift(1)
# Filter sequences where both candles are the same color
consecutive_candles = ranged_df[ranged_df['Current_Candle_color'] == ranged_df['Prev_Candle_color']]
consecutive_candles = consecutive_candles.copy()
# print("Filtered sequences:\n", consecutive_candles[:50])

# Compare sizes
consecutive_candles['Curr_compared_to_prev'] = consecutive_candles.apply(
    lambda row: 'Bigger' if row['Current_Body_Size'] > row['Prev_Body_Size'] else
                ('Smaller' if row['Current_Body_Size'] < row['Prev_Body_Size'] else 'Same'),
    axis=1
)
print('Size_Comparison:\n', consecutive_candles)

# Count occurrences of each comparison
comparison_counts = consecutive_candles['Curr_compared_to_prev'].value_counts(normalize=True)
print()
print("Comparison of second candle to the first in sequences:")
print(comparison_counts)
print()


# Count transitions
total_green = sum(ranged_df['Current_Candle_color'] == 'G')
total_red = sum(ranged_df['Current_Candle_color'] == 'R')

print("total_green: ", total_green)
print("total_red: ", total_red)

green_to_green = sum((ranged_df['Current_Candle_color'] == 'G') & (ranged_df['Current_Candle_color'].shift(-1) == 'G'))
red_to_red = sum((ranged_df['Current_Candle_color'] == 'R') & (ranged_df['Current_Candle_color'].shift(-1) == 'R'))

print(f'green to green: {green_to_green}')
print(f'red to red: {red_to_red}')

three_greens = sum((ranged_df['Current_Candle_color'] == 'G') & (ranged_df['Current_Candle_color'].shift(-1) == 'G') & (ranged_df['Current_Candle_color'].shift(-2) == 'G'))
three_reds = sum((ranged_df['Current_Candle_color'] == 'R') & (ranged_df['Current_Candle_color'].shift(-1) == 'R') & (ranged_df['Current_Candle_color'].shift(-2) == 'R'))


candles_number = 8


def count_consecutive_candles(df, column_name, color, num_candles):
    """
    Count the occurrences of a given color appearing consecutively for a given number of candles.

    :param df: DataFrame containing the data.
    :param column_name: Column name representing the candle colors.
    :param color: The color to count ('G' or 'R').
    :param num_candles: The number of consecutive candles to check.
    :return: The count of occurrences.
    """
    # Create a condition for num_candles consecutive candles of the same color
    condition = True
    for i in range(num_candles):
        condition &= df[column_name].shift(-i) == color

    # Count the number of times the condition is True
    return condition.sum()


# Example usage
green_to_green_count = count_consecutive_candles(ranged_df, 'Current_Candle_color', 'G', candles_number)
red_to_red_count = count_consecutive_candles(ranged_df, 'Current_Candle_color', 'R', candles_number)
print("--------------------------")
print(f"Green to green ({candles_number} candles): {green_to_green_count}")
print(f"Red to red ({candles_number} candles): {red_to_red_count}")
print("--------------------------")
print(f'three_greens: {three_greens}')
print(f'three_reds: {three_reds}')


# Calculate probabilities of two streak
p_green_to_green = green_to_green / total_green if total_green > 0 else 0
p_red_to_red = red_to_red / total_red if total_red > 0 else 0
# Calculate probabilities of three streak
p_three_greens = three_greens / total_green if total_green > 0 else 0
p_three_reds = three_reds / total_red if total_red > 0 else 0

print(f"Probability of (2) green streak: {p_green_to_green}")
print(f"Probability of (2) red streak: {p_red_to_red}")

print(f"Probability of (3) green streak: {p_three_greens}")
print(f"Probability of (3) three red streak: {p_three_reds}")

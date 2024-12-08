import pandas as pd

start_date = '2024-11-22 14:30'  # Choose the start date to begin from
end_date = '2024-11-22 21:00'  # Choose the end date

file_path = 'Bars/1430w.csv'

pd.set_option('display.max_rows', 100)  # Increase the number of rows shown
pd.set_option('display.max_columns', 8)  # Increase the number of columns shown
pd.set_option('display.width', 500)  # Increase the terminal width for better visibility


def get_dataframe_from_file(path):

    print()

    columns_to_parse = ['Date', 'Time', 'Open', 'High', 'Low', 'Close']
    csv_df = pd.read_csv(
        path,
        usecols=columns_to_parse
    )

    print()
    print('1. Source dataframe: \n', csv_df)
    return csv_df


dataframe_csv = get_dataframe_from_file(file_path)


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


ranged_dataframe = date_range_func(dataframe_csv, start_date, end_date)


def add_candles_colors_to_dataframe(ranged_df):
    # Determine candle color
    ranged_df['Current_Candle_color'] = ranged_df.apply(lambda row: 'G' if row['Close'] > row['Open'] else 'R', axis=1)
    print("All candle colors:\n", ranged_df[:25])

    # Calculate candle body sizes
    # ranged_df['Current_Body_Size'] = abs(ranged_df['High'] - ranged_df['Low'])
    # ranged_df['Prev_Body_Size'] = ranged_df['Current_Body_Size'].shift(1)

    # Identify sequences of two consecutive candles
    ranged_df['Prev_Candle_color'] = ranged_df['Current_Candle_color'].shift(1)
    print("Prev_Candle:\n", ranged_df[:25])

    # Count transitions
    tot_green = sum(ranged_df['Current_Candle_color'] == 'G')
    tot_red = sum(ranged_df['Current_Candle_color'] == 'R')

    print("total_green: ", tot_green)
    print("total_red: ", tot_red)

    g_to_g = sum((ranged_df['Current_Candle_color'] == 'G') & (ranged_df['Current_Candle_color'].shift(-1) == 'G'))
    r_to_r = sum((ranged_df['Current_Candle_color'] == 'R') & (ranged_df['Current_Candle_color'].shift(-1) == 'R'))

    print(f'green to green: {g_to_g}')
    print(f'red to red: {r_to_r}')

    three_g = sum((ranged_df['Current_Candle_color'] == 'G') & (ranged_df['Current_Candle_color'].shift(-1) == 'G') & (ranged_df['Current_Candle_color'].shift(-2) == 'G'))
    three_r = sum((ranged_df['Current_Candle_color'] == 'R') & (ranged_df['Current_Candle_color'].shift(-1) == 'R') & (ranged_df['Current_Candle_color'].shift(-2) == 'R'))

    return three_g, three_r, tot_green, tot_red, g_to_g, r_to_r


(
    three_greens,
    three_reds,
    total_green,
    total_red,
    green_to_green,
    red_to_red
) = add_candles_colors_to_dataframe(ranged_dataframe)


def build_transition_matrix(df, column_name):
    """
    Build a transition matrix for candle colors.

    :param df: DataFrame containing the data.
    :param column_name: Column name representing the candle colors.
    :return: A transition matrix as a DataFrame.
    """
    # States
    states = ['G', 'R']
    transition_counts = {state: {next_state: 0 for next_state in states} for state in states}

    # Count transitions
    for i in range(len(df) - 1):
        current_state = df.iloc[i][column_name]
        next_state = df.iloc[i + 1][column_name]
        if current_state in states and next_state in states:
            transition_counts[current_state][next_state] += 1

    # Convert counts to probabilities
    trans_matrix = pd.DataFrame(transition_counts).T
    trans_matrix = trans_matrix.div(trans_matrix.sum(axis=1), axis=0)

    return trans_matrix


# Build and display the transition matrix
transition_matrix = build_transition_matrix(ranged_dataframe, 'Current_Candle_color')
print("\nTransition Matrix:")
print(transition_matrix)


def predict_next_state(current_state, transition_matrix):
    """
    Predict the next state based on the current state and transition matrix.

    :param current_state: The current state ('G' or 'R').
    :param transition_matrix: The transition matrix as a DataFrame.
    :return: The predicted next state.
    """
    probabilities = transition_matrix.loc[current_state]
    return probabilities.idxmax()  # Return the state with the highest probability


# Example prediction
current_state = ranged_dataframe.iloc[-1]['Current_Candle_color']  # Last candle's color
predicted_state = predict_next_state(current_state, transition_matrix)
print(f"Current state: {current_state}, Predicted next state: {predicted_state}")


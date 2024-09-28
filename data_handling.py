import pandas as pd
import os

file_path = 'Bars/MESU24_M1_w.csv'


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
        print('2. Filtered dataframe: \n', df_filtered_by_date)
        return ticker, df_filtered_by_date      # DF MUST BE INDEX RESET


"""
In order to draw levels we need to resample M1 datapoints to H1
"""

#   RESAMPLE H1 FROM M1 DATAPOINTS


def resample_m1_datapoints(df_filtered_by_date):
    df_filtered_by_date.set_index('DateTime', inplace=True)  # Set index to DateTime for .agg function
    df_h1 = df_filtered_by_date.resample('H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })
    aggregated_filtered_h1_dataframe = df_h1.dropna()  # Remove NaN rows from the Dataframe
    print('3. Aggregated dataframe: \n', aggregated_filtered_h1_dataframe)
    return aggregated_filtered_h1_dataframe

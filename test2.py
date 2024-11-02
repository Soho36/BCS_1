import pandas as pd
# from test import levels_from_file

mt5_logging_file_path = (
    f'C:\\Users\\Vova deduskin lap\\AppData\\Roaming\\MetaQuotes\\Terminal\\'
    f'D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\OHLCVData_475.csv'
)


def get_dataframe_from_file():
    log_df = pd.read_csv(mt5_logging_file_path, sep=';', encoding='utf-16', engine='python')
    new_column_names = ['Ticker', 'Timeframe', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    log_df.columns = new_column_names
    log_df['Datetime'] = pd.to_datetime(log_df['Date'] + ' ' + log_df['Time'], format='ISO8601')
    log_df.set_index('Datetime', inplace=True)
    dataframe_from_log = log_df.loc[:, ['Ticker', 'Date', 'Time', 'Open', 'High', 'Low', 'Close']]
    datetime_index = log_df.index
    first_date = datetime_index[0]
    first_date2 = str(first_date)

    return dataframe_from_log, first_date, first_date2


df, first_date, first_date2 = get_dataframe_from_file()
print(df)
print(first_date2)


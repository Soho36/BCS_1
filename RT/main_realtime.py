from RT.data_handling_realtime import get_dataframe_from_file
from price_levels_manual_realtime import process_levels
from signals_with_ob_short_long_realtime import level_rejection_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 0.01                 # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio
stop_loss_offset = 20               # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

hardcoded_sr_levels = [
    ('2024-11-01 11:12:00', 69053.00),
    ('2024-11-01 11:12:00', 68797.00),
    ('2024-11-01 11:12:00', 69639.00),
    ('2024-11-01 11:12:00', 70585.00),
    ('2024-11-01 11:12:00', 68398.00),
]  # Example support levels

level_interactions_threshold = 2
max_time_waiting_for_entry = 10

# **************************************************************************************************************

path = 'C:\\Users\\Liikurserv\\AppData\\Roaming\\MetaQuotes\\Terminal\\1D0E83E0BCAA42603583233CF21A762C\\MQL5\\Files'
file = 'OHLCVData_475.csv'


buy_signal_flag = True                    # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_flag = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
last_signal = None                              # Initiate last signal

"""
Watchdog module monitors csv changes for adding new OHLC row and trigger main.py function calls 
only when new data is added to the CSV
"""


class CsvChangeHandler(FileSystemEventHandler):
    print("\nScript successfully started. Waiting for first candle to close...".upper())

    def on_modified(self, event):
        global buy_signal_flag, sell_signal_flag, last_signal
        print(f"File modified: {event.src_path}")  # This should print on any modification
        if not event.src_path == os.path.join(path, file):  # CSV file path
            return
        print("CSV file updated; triggering function calls...")
        # Call a function that contains all main calls
        buy_signal_flag, sell_signal_flag, last_signal = run_main_functions(
            buy_signal_flag, sell_signal_flag, last_signal
        )


def run_main_functions(b_s_flag, s_s_flag, l_signal):
    print('\n---------------------------------------------------------------------------------------------------------')
    # GET DATAFRAME FROM LOG
    dataframe_from_log = get_dataframe_from_file()
    print('\nget_dataframe_from_file: \n', dataframe_from_log[-10:])

    # PRICE LEVELS
    (
        levels_startpoints_to_chart,
        levels_endpoints_to_chart,
        level_discovery_signals_series_out,
        sr_levels,
        output_df_with_levels
    ) = process_levels(
        dataframe_from_log,
        hardcoded_sr_levels
    )
    print('\noutput_df_with_levels2: \n', output_df_with_levels[-10:])

    # SIGNALS

    (
        over_under_counter,
        s_signal,
        n_index
    ) = level_rejection_signals(
        output_df_with_levels,
        sr_levels,
        level_interactions_threshold,
        max_time_waiting_for_entry
    )
    # print(f'\n!!!!!s_signal: {s_signal}\n')

    # LAST CANDLE OHLC (current OHLC)
    (
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker
     ) = last_candle_ohlc(
        output_df_with_levels
    )

    # TRANSMITTER FUNCTION

    # SEND ORDERS
    (
        b_s_flag,
        s_s_flag,
    ) = send_buy_sell_orders(
        l_signal,
        s_signal,
        n_index,
        b_s_flag,
        s_s_flag,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward,
    )

    l_signal = s_signal
    return b_s_flag, s_s_flag, l_signal


if __name__ == "__main__":
    event_handler = CsvChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)  # CSV folder path
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print('Program stopped manually'.upper())
        observer.stop()
    observer.join()

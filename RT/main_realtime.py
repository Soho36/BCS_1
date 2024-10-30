from RT.data_handling_realtime import get_dataframe_from_file
from price_levels_manual_realtime import process_levels
from signals_with_ob_short_long_realtime import level_rejection_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
import time

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 0.01                 # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio
stop_loss_offset = 10               # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

hardcoded_sr_levels = [
    ('2024-10-31 00:37:00', 72363.56),
    ('2024-10-31 00:37:00', 72308.00),
]  # Example support levels

level_interactions_threshold = 3
max_time_waiting_for_entry = 10

# **************************************************************************************************************
log_file_reading_interval = 1                   # File reading interval (sec)

buy_signal_discovered = True                    # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_discovered = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
last_signal = None                              # Initiate last signal

try:
    while True:

        # GET DATAFRAME FROM LOG
        dataframe_from_log = get_dataframe_from_file()
        print('\nget_dataframe_from_file: \n', dataframe_from_log)

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
        print('\noutput_df_with_levels2: \n', output_df_with_levels)

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
        print(f'\n!!!!!s_signal: {s_signal}\n')

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
            buy_signal_discovered,
            sell_signal_discovered,
        ) = send_buy_sell_orders(
            last_signal,
            s_signal,
            n_index,
            buy_signal_discovered,
            sell_signal_discovered,
            last_candle_high,
            last_candle_low,
            last_candle_close,
            ticker,
            stop_loss_offset,
            risk_reward,
        )
        last_signal = s_signal
        time.sleep(log_file_reading_interval)   # Pause between reading

except KeyboardInterrupt:
    print()
    print('Program stopped manually'.upper())

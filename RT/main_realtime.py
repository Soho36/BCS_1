from RT.data_handling_realtime import get_dataframe_from_file
from price_levels_manual_realtime import process_levels
from signals_with_ob_short_long_realtime import level_rejection_signals
from orders_sender import last_candle_ohlc, send_buy_sell_orders
import time

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 0.01                 # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio
stop_loss_offset = 10               # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

# hardcoded_sr_levels = [
#     ('2024-10-23 19:29:00', 20394.00),
# ]  # Example support levels

hardcoded_sr_levels = [
    ('2024-10-28 00:52:00', 68128.00),
    ('2024-10-28 00:52:00', 68088.00),
]  # Example support levels

level_interactions_threshold = 1
max_time_waiting_for_entry = 10

# **************************************************************************************************************
log_file_reading_interval = 1       # File reading interval (sec)

buy_signal_discovered = True                   # MUST BE TRUE BEFORE ENTERING MAIN LOOP
sell_signal_discovered = True                  # MUST BE TRUE BEFORE ENTERING MAIN LOOP

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
            signals_to_order_sender_series,
            actual_signals_series_with_prices,  # Actual signals for placing a trade
            yellow_star_signals_series_with_prices,
            over_under_counter,
            s_signal
        ) = level_rejection_signals(
            output_df_with_levels,
            sr_levels,
            level_interactions_threshold,
            max_time_waiting_for_entry
        )
        print(f'\ns_signal: {s_signal}\n')
        # print('\nsignals_to_order_sender_series: \n', signals_to_order_sender_series)
        # print('\nactual_signals_series_with_prices: \n', actual_signals_series_with_prices)

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
            s_signal,
            buy_signal_discovered,
            sell_signal_discovered,
            last_candle_high,
            last_candle_low,
            last_candle_close,
            ticker,
            stop_loss_offset,
            risk_reward,
        )

        time.sleep(log_file_reading_interval)   # Pause between reading

except KeyboardInterrupt:
    print()
    print('Program stopped manually'.upper())

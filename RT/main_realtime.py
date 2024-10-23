from RT.data_handling_realtime import get_dataframe_from_file
from price_levels_manual_realtime import process_levels
# from signals_with_ob_short_long_realtime import level_rejection_signals
import time

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 0.01                 # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio
stop_loss_offset = 10               # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

hardcoded_sr_levels = [
    ('2024-10-22 22:17:00', 20507.00),
    ('2024-10-23 19:07:00', 20174.00),
]  # Example support levels

level_interactions_threshold = 1
max_time_waiting_for_entry = 10

# **************************************************************************************************************
log_file_reading_interval = 1       # File reading interval (sec)

# GET DATAFRAME FROM LOG
dataframe_from_log = get_dataframe_from_file()

# LAST CANDLE OHLC (current OHLC)
# (
#     last_candle_open,
#     last_candle_high,
#     last_candle_low,
#     last_candle_close,
#     ticker
#  ) = last_candle_ohlc(
#     dataframe_from_log
# )

# PRICE LEVELS
(
    levels_startpoints_to_chart,
    levels_endpoints_to_chart,
    level_discovery_signals_series_out,
    sr_levels_out,
    output_df_with_levels
) = process_levels(
    dataframe_from_log,
    hardcoded_sr_levels
)

# SIGNALS

# (
#     rejection_signals_series_outside,
#     yellow_star_signals_series_with_prices,
#     rejection_signals_series_for_chart_outside,
#     ob_candle_series_for_chart,
#     under_over_series_for_chart,
#     over_under_counter
# ) = level_rejection_signals(
#     dataframe_from_log,
#     sr_levels,
#     level_interactions_threshold,
#     max_time_waiting_for_entry
# )


# SEND ORDERS
# (buy_signal_discovered,
#  sell_signal_discovered) = send_buy_sell_orders(buy_signal,
#                                                 sell_signal,
#                                                 last_candle_open,
#                                                 last_candle_high,
#                                                 last_candle_low,
#                                                 last_candle_close,
#                                                 ticker)
#
time.sleep(log_file_reading_interval)   # Pause between reading

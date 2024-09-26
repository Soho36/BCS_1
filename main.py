# import pandas as pd
from data_handling import getting_dataframe_from_file, date_range_func, resample_m1_datapoints
from price_levels import process_levels
from signals import level_rejection_signals
from trade_simulation import trades_simulation

# **************************************** SETTINGS **************************************
file_path = 'Bars/MESU24_M1_w.csv'

# Get the data
dataframe_from_csv = getting_dataframe_from_file(file_path)
print('Source dataframe: \n', dataframe_from_csv)

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

# ********************************************************************************************************************
# FUNCTIONS CALLS

# Filter by date
ticker_name, filtered_by_date_dataframe = date_range_func(dataframe_from_csv, start_date, end_date)

# Resample to H1
aggregated_filtered_df = resample_m1_datapoints(filtered_by_date_dataframe)
print('Aggregated dataframe: \n', aggregated_filtered_df)

filtered_by_date_dataframe_original = filtered_by_date_dataframe.copy()     # Passed to Simulation
print('Copy of original: \n', filtered_by_date_dataframe_original)

# Call process_levels function in price_levels, get levels points for chart
(
    levels_startpoints_to_chart,
    levels_endpoints_to_chart,
    support_level_signal_running_out,
    resistance_level_signal_running_out,
    level_discovery_signals_series_out,
    sr_levels_out
) = process_levels(aggregated_filtered_df)

levels_points_for_chart = [[a, b] for a, b in zip(levels_startpoints_to_chart, levels_endpoints_to_chart)]

rejection_signals_series_outside, rejection_signals_series_for_chart_outside = (
    level_rejection_signals(filtered_by_date_dataframe, sr_levels_out)
)
print('Rejection_signals_series: \n', rejection_signals_series_outside)


#   SIMULATION FUNCTION CALL
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
    stop_loss_offset_multiplier,
    rejection_signals_series_outside
)
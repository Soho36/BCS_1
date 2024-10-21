from data_handling import getting_dataframe_from_file, date_range_func, resample_m1_datapoints
# from price_levels import process_levels
# from pivots import process_levels
from price_levels_manual import process_levels
"""
sig3 works interesting on hourly. draw too much levels (need to exclude premarket)
enable 1minute simulation but on 1H OHLC (what happened first SL or TP)
manual level entry as option to find out will it be more precise -> better outcome?
"""
# from signals import level_rejection_signals
# from signals_with_OB import level_rejection_signals
# from signals_with_OB_GPT import level_rejection_signals
from signals_with_ob_short_long import level_rejection_signals


from simulation import trades_simulation
# from trade_simulation_next_candle import trades_simulation
from analysis import trades_analysis
from analysis_charts import plot_line_chart_balance_change, plot_line_chart_profits_losses
import matplotlib.pyplot as plt
from candlestick_chart import plot_candlestick_chart, plot_candlestick_chart_1h


# =====================================================================================================================
# SETTINGS
# =====================================================================================================================
# Get the data
# file_path = 'Bars/MESZ24_M1_202409160000_202409272059_w.csv'
# file_path = 'Bars/2MESZ24_M1_202409160000_202409272059_w.csv'
# file_path = 'Bars/MESZ24_H1_w.csv'
file_path = 'Bars/MESZ24_M1_0801_w.csv'

dataframe_from_csv = getting_dataframe_from_file(file_path)

start_date = '2024-09-18'  # Choose the start date to begin from
end_date = '2024-09-18'  # Choose the end date

# Manually define the support and resistance levels
# Format: [(index_or_datetime, price_level)]

hardcoded_sr_levels = [
    ('2024-09-18 08:30:00', 5698.40),
    ('2024-09-18 06:30:00', 5711.00),
    ('2024-09-18 12:30:00', 5699.30),
    ('2024-09-18 16:30:00', 5682.50),
    ('2024-09-18 17:30:00', 5711.90),
    # ('2024-09-17 16:30:00', 5679.70),
    # ('2024-09-17 17:33:00', 5700.47)
]  # Example support levels

# SIMULATION
start_simulation = True

# ENTRY CONDITIONS
level_interactions_threshold = 1
max_time_waiting_for_entry = 20
use_candle_close_as_entry = True  # Must be False if next condition is True
use_level_price_as_entry = False  # Must be False if previous condition is True
confirmation_close = False  # Candle close above/below level as confirmation
longs_allowed = True  # Allow or disallow trade direction
shorts_allowed = True  # Allow or disallow trade direction

# RISK MANAGEMENT

spread = 0
risk_reward_ratio = 1  # Chose risk/reward ratio (aiming to win compared to lose)
stop_loss_as_candle_min_max = True
stop_loss_offset = 0.1  # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)
# HAS TO BE >0 TO AVOID BOTH TRADES

stop_loss_price_as_dollar_amount = False  # STOP as distance from entry price (previous must be false)
rr_dollar_amount = 2  # Value for stop as distance

stop_loss_as_plus_candle = False
stop_loss_offset_multiplier = 0  # 1 places stop one candle away from H/L (only when stop_loss_as_plus_candle = True

# CHARTS
show_candlestick_chart_m1 = True
show_candlestick_chart_H1 = True
show_level_rejection_signals = True
find_levels = True
show_profits_losses_line_chart = False  # Only when Simulation is True
show_balance_change_line_chart = False  # Only when Simulation is True

# =====================================================================================================================
# FUNCTIONS CALLS
# =====================================================================================================================
# data_handling.py
ticker_name, filtered_by_date_dataframe_m1 = date_range_func(
    dataframe_from_csv,
    start_date,
    end_date
)

# Resample to H1
aggregated_filtered_dataframe_h1 = resample_m1_datapoints(filtered_by_date_dataframe_m1)

# price_levels.py
# Call process_levels function in price_levels, get levels points for chart
(
    levels_startpoints_to_chart,
    levels_endpoints_to_chart,
    # support_level_signal_running_out,
    # resistance_level_signal_running_out,
    level_discovery_signals_series_out,
    sr_levels_out,
    output_df_with_levels
) = process_levels(
    filtered_by_date_dataframe_m1,
    aggregated_filtered_dataframe_h1,
    hardcoded_sr_levels
)

# print('55. support_level_signal_running_out', support_level_signal_running_out)
# print('66. resistance_level_signal_running_out', resistance_level_signal_running_out)
print('77.sr_levels_out', sr_levels_out)


#   Will be used in charting:
levels_points_for_chart = [[a, b] for a, b in zip(levels_startpoints_to_chart, levels_endpoints_to_chart)]

print('44. levels_points_for_chart: \n', levels_points_for_chart)

(
    rejection_signals_series_outside,
    yellow_star_signals_series_with_prices,
    rejection_signals_series_for_chart_outside,
    ob_candle_series_for_chart,
    under_over_series_for_chart,
    over_under_counter
) = level_rejection_signals(
    output_df_with_levels,
    sr_levels_out,
    level_interactions_threshold,
    max_time_waiting_for_entry
)

print('Rejection_signals_series: \n', rejection_signals_series_outside)     # THIS SERIES GOES TO SIMULATION

# =====================================================================================================================
#   SIMULATION FUNCTION CALL
# =====================================================================================================================
filtered_by_date_dataframe_original = filtered_by_date_dataframe_m1.copy()  # Passed to Simulation
# print('Copy of original: \n', filtered_by_date_dataframe_original)
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
    start_simulation,
    longs_allowed,
    shorts_allowed,
    use_level_price_as_entry,
    use_candle_close_as_entry,
    stop_loss_as_candle_min_max,
    stop_loss_offset,
    stop_loss_price_as_dollar_amount,
    rr_dollar_amount,
    risk_reward_ratio,
    stop_loss_as_plus_candle,
    spread,
    risk_reward_ratio,
    stop_loss_offset_multiplier,
    rejection_signals_series_outside,
    # yellow_star_signals_series_with_prices,   # Supposed to be for SL at OB candle... Not in use so far
)
# =====================================================================================================================
#   ANALYSIS FUNCTION CALL
# =====================================================================================================================
(
    rounded_trades_list_to_chart_profits_losses,
    rounded_results_as_balance_change_to_chart_profits
) = trades_analysis(
    trade_result_both_to_trade_analysis,
    trade_results_to_trade_analysis,
    trades_counter_to_trade_analysis,
    trade_direction_to_trade_analysis,
    profit_loss_long_short_to_trade_analysis,
    trade_result_longs_to_trade_analysis,
    trade_result_shorts_to_trade_analysis,
    dataframe_from_csv,
    start_simulation,
    start_date,
    end_date,
    spread,
    filtered_by_date_dataframe_m1,
    risk_reward_ratio,
    ticker_name
)

# =====================================================================================================================
#       LINE CHARTS CALLS
# =====================================================================================================================
plot_line_chart_balance_change(
    rounded_results_as_balance_change_to_chart_profits,
    start_simulation,
    show_balance_change_line_chart,
    start_date,
    end_date,
    ticker_name
)
plot_line_chart_profits_losses(
    rounded_trades_list_to_chart_profits_losses,
    start_simulation,
    show_profits_losses_line_chart
)
# =====================================================================================================================
#       CANDLESTICK CHART CALL
# =====================================================================================================================
try:
    plot_candlestick_chart(  # 1-minute chart
        filtered_by_date_dataframe_m1,
        level_discovery_signals_series_out,
        rejection_signals_series_for_chart_outside,
        ob_candle_series_for_chart,
        under_over_series_for_chart,
        show_candlestick_chart_m1,
        find_levels,
        levels_points_for_chart,
        ticker_name
    )

except KeyboardInterrupt:
    print('Program stopped manually')

try:
    plot_candlestick_chart_1h(  # 1h-chart
        aggregated_filtered_dataframe_h1,
        # level_discovery_signals_series_out,
        # rejection_signals_series_for_chart_outside,
        show_candlestick_chart_H1,
        find_levels,
        levels_points_for_chart,
        ticker_name
    )

except KeyboardInterrupt:
    print('Program stopped manually')

plt.show()  # Show all charts


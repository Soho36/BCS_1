from data_handling import getting_dataframe_from_file, date_range_func, resample_m1_datapoints
from price_levels import process_levels
from signals import level_rejection_signals
from trade_simulation import trades_simulation
from trade_analysis import trades_analysis
from analysis_charts import plot_line_chart_balance_change, plot_line_chart_profits_losses
import matplotlib.pyplot as plt
from candlestick_chart import plot_candlestick_chart, plot_candlestick_chart_1h

# =====================================================================================================================
# SETTINGS
# =====================================================================================================================
# Get the data
file_path = 'Bars/MESZ24_M1_202409160000_202409272059_w.csv'
dataframe_from_csv = getting_dataframe_from_file(file_path)

start_date = '2024-09-16'       # Choose the start date to begin from
end_date = '2024-09-16'         # Choose the end date

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
stop_loss_as_candle_min_max = True
stop_loss_offset = 0                 # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

stop_loss_price_as_dollar_amount = False   # STOP as distance from entry price (previous must be false)
rr_dollar_amount = 2                       # Value for stop as distance

stop_loss_as_plus_candle = False
stop_loss_offset_multiplier = 0    # 1 places stop one candle away from H/L (only when stop_loss_as_plus_candle = True


# CHARTS
show_candlestick_chart = True
show_level_rejection_signals = True
find_levels = True
show_profits_losses_line_chart = False  # Only when Simulation is True
show_balance_change_line_chart = False   # Only when Simulation is True

# =====================================================================================================================
# FUNCTIONS CALLS
# =====================================================================================================================
# data_handling.py
ticker_name, filtered_by_date_dataframe = date_range_func(
        dataframe_from_csv,
        start_date,
        end_date
)

# Resample to H1
aggregated_filtered_h1_dataframe = resample_m1_datapoints(filtered_by_date_dataframe)

# price_levels.py
# Call process_levels function in price_levels, get levels points for chart
(
        levels_startpoints_to_chart,
        levels_endpoints_to_chart,
        support_level_signal_running_out,
        resistance_level_signal_running_out,
        level_discovery_signals_series_out,
        sr_levels_out,
        aggregated_filtered_df,
        output_df_with_levels
) = process_levels(
        filtered_by_date_dataframe,
        aggregated_filtered_h1_dataframe
)

#   Will be used in charting:
levels_points_for_chart = [[a, b] for a, b in zip(levels_startpoints_to_chart, levels_endpoints_to_chart)]
print('levels_points_for_chart: \n', levels_points_for_chart)

(
        rejection_signals_series_outside,
        rejection_signals_series_for_chart_outside
) = level_rejection_signals(
        output_df_with_levels,
        sr_levels_out,
        use_level_price_as_entry,
        use_candle_close_as_entry
)

print('Rejection_signals_series: \n', rejection_signals_series_outside)

# =====================================================================================================================
#   SIMULATION FUNCTION CALL
# =====================================================================================================================
filtered_by_date_dataframe_original = filtered_by_date_dataframe.copy()     # Passed to Simulation
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
        new_trades_threshold,
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
        rejection_signals_series_outside
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
        filtered_by_date_dataframe,
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
    plot_candlestick_chart(             # 1-minute chart
        filtered_by_date_dataframe,
        level_discovery_signals_series_out,
        rejection_signals_series_for_chart_outside,
        show_candlestick_chart,
        find_levels,
        levels_points_for_chart,
        ticker_name
    )

except KeyboardInterrupt:
    print('Program stopped manually')

try:
    plot_candlestick_chart_1h(          # 1h-chart
        aggregated_filtered_h1_dataframe,
        # level_discovery_signals_series_out,
        # rejection_signals_series_for_chart_outside,
        show_candlestick_chart,
        find_levels,
        levels_points_for_chart,
        ticker_name
    )

except KeyboardInterrupt:
    print('Program stopped manually')

plt.show()  # Show all charts

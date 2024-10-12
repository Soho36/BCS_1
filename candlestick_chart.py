import mplfinance as mpf
import numpy as np
import pandas as pd

# =====================================================================================================================
# 1 - MINUTE CHART
# =====================================================================================================================


def plot_candlestick_chart(
        df,
        level_discovery_signals_series,
        rejection_signals_series,
        ob_candle_series_for_chart,
        show_candlestick_chart_m1,
        find_levels,
        levels_points_for_chart,
        ticker_name
):

    print('CHART DF: \n', df)
    print('CHART level_discovery_signals_series: \n', level_discovery_signals_series)
    print('CHART rejection_signals_series: \n', rejection_signals_series)

    if show_candlestick_chart_m1:

        plots_list = []
        # Create an empty series with NaN values, having the same index as your original DataFrame df:
        signal_series_for_chart = pd.Series([np.nan] * len(df), index=df.index)
        ob_candle_series_for_chart2 = pd.Series([np.nan] * len(df), index=df.index)

        # Populate signal series with valid signals
        for signal_index, signal_value in rejection_signals_series:
            if signal_value == -100 or signal_value == 100:  # Check if the signal value is valid
                signal_series_for_chart.iloc[signal_index] = signal_value

        # Append once, after filling the series
        if not signal_series_for_chart.isna().all():
            plots_list.append(
                mpf.make_addplot(
                    signal_series_for_chart,
                    type='scatter',
                    color='black',
                    markersize=250,
                    marker='+',
                    panel=1
                )
            )
        else:
            print("No valid signals to plot.")

        for signal_index, signal_value in ob_candle_series_for_chart:
            if signal_value == -10 or signal_value == 10:  # Check if the signal value is valid
                ob_candle_series_for_chart2.iloc[signal_index] = signal_value

        # Append once, after filling the series
        if not ob_candle_series_for_chart2.isna().all():
            plots_list.append(
                mpf.make_addplot(
                    ob_candle_series_for_chart2,
                    type='scatter',
                    color='green',
                    markersize=250,
                    marker='*',
                    panel=1
                )
            )
        else:
            print("No valid signals to plot.")

        if find_levels:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                alines=dict(alines=levels_points_for_chart, linewidths=2, alpha=0.4),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list,
                block=False
            )
        else:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list,
                block=False
            )


# =====================================================================================================================
# HOURLY CHART
# =====================================================================================================================


def plot_candlestick_chart_1h(
        aggregated_filtered_h1_dataframe,
        # level_discovery_signals_series,
        # rejection_signals_series,
        show_candlestick_chart_h1,
        find_levels,
        levels_points_for_chart,
        ticker_name
):

    print('CHART DF 1h: \n', aggregated_filtered_h1_dataframe)
    # print('CHART level_discovery_signals_series: \n', level_discovery_signals_series)
    # print('CHART rejection_signals_series: \n', rejection_signals_series)

    if show_candlestick_chart_h1:

        plots_list = []

        print()

        if find_levels:
            mpf.plot(
                aggregated_filtered_h1_dataframe,
                type='candle',
                figsize=(12, 6),
                alines=dict(alines=levels_points_for_chart, linewidths=2, alpha=0.4),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list,
                block=False
            )

        else:
            mpf.plot(
                aggregated_filtered_h1_dataframe,
                type='candle',
                figsize=(12, 6),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list,
                block=False
            )

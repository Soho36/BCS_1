import mplfinance as mpf


def plot_candlestick_chart(
        df,
        level_discovery_signals_series,
        rejection_signals_series,
        show_candlestick_chart,
        find_levels,
        levels_points_for_chart,
        ticker_name,



):
    print('CHART DF: \n', df)
    print('CHART level_discovery_signals_series: \n', level_discovery_signals_series)
    print('CHART rejection_signals_series: \n', rejection_signals_series)

    if show_candlestick_chart:

        # df.set_index('Datetime', inplace=True)
        plots_list = []

        # for i, s in enumerate(level_discovery_signals_series):
        #     if s != 'NaN':
        #         plots_list.append(
        #             mpf.make_addplot(
        #                 level_discovery_signals_series,
        #                 type='scatter',
        #                 color='black',
        #                 markersize=250,
        #                 marker='*',
        #                 panel=1
        #             )
        #         )

        for i, s in enumerate(rejection_signals_series):
            if s != 'NaN':
                plots_list.append(
                    mpf.make_addplot(
                        rejection_signals_series,
                        type='scatter',
                        color='black',
                        markersize=250,
                        marker='+',
                        panel=1))

        print()

        if find_levels:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                alines=dict(alines=levels_points_for_chart, linewidths=2, alpha=0.4),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list
            )

        else:
            mpf.plot(
                df,
                type='candle',
                figsize=(12, 6),
                style='yahoo',
                title=f'{ticker_name}'.upper(),
                addplot=plots_list
            )

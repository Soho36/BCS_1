import pandas as pd


def trades_simulation(
        filtered_df_original,
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
        risk_reward_simulation,
        sl_offset_multiplier,
        rejection_signals_series_with_prices,
        yellow_star_signals_series_with_prices,     # Pass signals with prices for OB candle SL implementation
):

    #   Convert Date column to Datetime object
    filtered_df_original['Date'] = pd.to_datetime(filtered_df_original['Date'])
    filtered_df_original.reset_index(inplace=True)
    if start_simulation:
        trades_counter = 0
        trade_result_both = []
        trade_result = []
        trade_result_longs = []
        trade_result_shorts = []
        trade_direction = []
        profit_loss_long_short = []     # List of profits and losses by longs and shorts

        signal_series = rejection_signals_series_with_prices
        print('signal_series', signal_series)
        yellow_star_signals_series_with_prices = yellow_star_signals_series_with_prices

        # print('signal_yellow_star_series', yellow_star_signals_series_with_prices)

        """
        Now we need somehow get entry price from signal series, but stop loss price from 
        yellow_star_signals_series_with_prices???
        """
        for (signal_index, signal_value, price_level) in signal_series:

            # LONG TRADES LOGIC
            if signal_value == 100 and longs_allowed:

                trades_counter += 1
                trade_direction.append('Long')
                signal_candle_date = (filtered_df_original.iloc[signal_index]['Date']).strftime('%Y-%m-%d')
                signal_candle_time = filtered_df_original.iloc[signal_index]['Time']
                signal_candle_low = round(filtered_df_original.iloc[signal_index]['Low'], 3)

                if use_level_price_as_entry:
                    entry_price = price_level

                elif use_candle_close_as_entry:
                    entry_price = round(filtered_df_original.iloc[signal_index]['Close'], 3)   # ENTRY

                else:
                    entry_price = None
                    print("Choose entry type".upper())

                stop_loss_price = None
                take_profit_price = None

                if stop_loss_as_candle_min_max:  # STOP as candle low
                    stop_loss_price = (signal_candle_low - stop_loss_offset)
                    take_profit_price = (
                            (((entry_price - stop_loss_price) * risk_reward_simulation)
                             + entry_price) + stop_loss_offset
                    )

                elif stop_loss_price_as_dollar_amount:  # STOP as distance from entry price
                    stop_loss_price = entry_price - rr_dollar_amount
                    take_profit_price = entry_price + (rr_dollar_amount * risk_reward_ratio)

                elif stop_loss_as_plus_candle:
                    stop_loss_price = (signal_candle_low - ((entry_price - signal_candle_low)
                                                            * sl_offset_multiplier))
                    take_profit_price = (((entry_price - stop_loss_price) * risk_reward_simulation) +
                                         entry_price)
                else:
                    print('Stop loss condition is not properly defined')

                print('------------------------------------------------------------------------------------------')
                print(f'▲ ▲ ▲ OPEN LONG TRADE: ▲ ▲ ▲ {signal_candle_date} {signal_candle_time}')
                print(f'Entry price: {entry_price}')
                print(f'Take: {round(take_profit_price, 3)} ({risk_reward_simulation}RR)')
                print(f'Stop: {stop_loss_price}')

                print()

                for j in range(signal_index, len(filtered_df_original)):
                    current_candle_date = (filtered_df_original.iloc[j]['Date']).strftime('%Y-%m-%d')
                    current_candle_time = (filtered_df_original.iloc[j]['Time'])
                    current_candle_open = filtered_df_original.iloc[j]['Open']
                    current_candle_high = filtered_df_original.iloc[j]['High']
                    current_candle_low = filtered_df_original.iloc[j]['Low']
                    current_candle_close = filtered_df_original.iloc[j]['Close']

                    print('Next candle: ', current_candle_date, current_candle_time, '|',
                          'O', current_candle_open,
                          'H', current_candle_high,
                          'L', current_candle_low,
                          'C', current_candle_close)

                    if current_candle_low <= stop_loss_price and current_candle_high >= take_profit_price:
                        trade_result_both.append(1)
                        print('!!! BOTH !!!')

                    if current_candle_low <= stop_loss_price:
                        trade_result.append((stop_loss_price - spread) -
                                            (entry_price + spread))
                        trade_result_longs.append((stop_loss_price - spread) -
                                                  (entry_price + spread))
                        profit_loss_long_short.append('LongLoss')
                        print(f'□ □ □ Stop Loss hit □ □ □ at {current_candle_date} {current_candle_time}')
                        print()
                        print(f'Trade Close Price: {round(stop_loss_price, 3)}')

                        print(
                          f'P/L: ${round((stop_loss_price - spread) - (entry_price + spread), 3)}'
                        )
                        print(
                            '---------------------------------------------'
                            '---------------------------------------------'
                        )
                        break

                    elif current_candle_high >= take_profit_price:
                        trade_result.append(take_profit_price - (entry_price + spread))
                        trade_result_longs.append(take_profit_price - (entry_price + spread))
                        profit_loss_long_short.append('LongProfit')
                        print(f'○ ○ ○ Take profit hit ○ ○ ○ at {current_candle_date} {current_candle_time}')
                        print()
                        print(f'Trade Trade Close Price: {round(take_profit_price, 3)}')

                        print(f'P/L: ${round(take_profit_price - (entry_price + spread), 3)}')
                        print(
                            '---------------------------------------------'
                            '---------------------------------------------'
                        )
                        break

                    else:
                        pass

            # SHORT TRADES LOGIC
            elif signal_value == -100 and shorts_allowed:

                trades_counter += 1
                trade_direction.append('Short')
                signal_candle_date = (filtered_df_original.iloc[signal_index]['Date']).strftime('%Y-%m-%d')
                signal_candle_time = filtered_df_original.iloc[signal_index]['Time']
                signal_candle_high = round(filtered_df_original.iloc[signal_index]['High'], 3)

                if use_level_price_as_entry:
                    entry_price = price_level

                elif use_candle_close_as_entry:
                    entry_price = round(filtered_df_original.iloc[signal_index]['Close'], 3)   # ENTRY

                else:
                    entry_price = None
                    print("Choose entry type".upper())

                stop_loss_price = None
                take_profit_price = None

                if stop_loss_as_candle_min_max:
                    stop_loss_price = signal_candle_high + stop_loss_offset
                    take_profit_price = ((entry_price -
                                          ((stop_loss_price - entry_price)
                                           * risk_reward_simulation))) - stop_loss_offset

                elif stop_loss_price_as_dollar_amount:  # STOP as distance from entry price
                    stop_loss_price = entry_price + rr_dollar_amount
                    take_profit_price = entry_price - (rr_dollar_amount * risk_reward_ratio)

                elif stop_loss_as_plus_candle:
                    # Adding size of the signal candle to the stop
                    stop_loss_price = (signal_candle_high +
                                       ((signal_candle_high - entry_price)
                                        * sl_offset_multiplier))
                    take_profit_price = (entry_price -
                                         ((stop_loss_price - entry_price) * risk_reward_simulation))
                else:
                    print('Stop loss condition is not properly defined')

                print('------------------------------------------------------------------------------------------')
                print(f'▼ ▼ ▼ OPEN SHORT TRADE: ▼ ▼ ▼ {signal_candle_date} {signal_candle_time}')
                print(f'Entry price: {entry_price}')
                print(f'Stop: {stop_loss_price}')
                print(f'Take: {round(take_profit_price, 3)} ({risk_reward_simulation}RR)')

                print()

                for j in range(signal_index, len(filtered_df_original)):
                    current_candle_date = (filtered_df_original.iloc[j]['Date']).strftime('%Y-%m-%d')
                    current_candle_time = (filtered_df_original.iloc[j]['Time'])
                    current_candle_open = filtered_df_original.iloc[j]['Open']
                    current_candle_high = filtered_df_original.iloc[j]['High']
                    current_candle_low = filtered_df_original.iloc[j]['Low']
                    current_candle_close = filtered_df_original.iloc[j]['Close']

                    print('Next candle: ', current_candle_date, current_candle_time, '|',
                          'O', current_candle_open,
                          'H', current_candle_high,
                          'L', current_candle_low,
                          'C', current_candle_close)

                    if current_candle_high >= stop_loss_price and current_candle_low <= take_profit_price:
                        trade_result_both.append(1)
                        print('BOTH')

                    if current_candle_high >= stop_loss_price:
                        trade_result.append((entry_price - spread) -
                                            (stop_loss_price + spread))
                        trade_result_shorts.append((entry_price - spread) -
                                                   (stop_loss_price + spread))
                        profit_loss_long_short.append('ShortLoss')
                        print(f'□ □ □ Stop Loss hit □ □ □ at {current_candle_date} {current_candle_time}')
                        print()
                        print(f'Trade Close Price: {round(stop_loss_price, 3)}')

                        print(
                          f'P/L: ${round((entry_price - spread) - (stop_loss_price + spread), 3)}'
                        )
                        print(
                            '---------------------------------------------'
                            '---------------------------------------------'
                        )
                        break

                    elif current_candle_low <= take_profit_price:
                        trade_result.append((entry_price - spread) - take_profit_price)
                        trade_result_shorts.append((entry_price - spread) - take_profit_price)
                        profit_loss_long_short.append('ShortProfit')
                        print(f'○ ○ ○ Take profit hit ○ ○ ○ at {current_candle_date} {current_candle_time}')
                        print()
                        print(f'Trade Close Price: {round(take_profit_price, 3)}')

                        print(f'P/L: ${round((entry_price - spread) - take_profit_price, 3)}')
                        print(
                            '---------------------------------------------'
                            '---------------------------------------------'
                        )

                        break

                    else:
                        pass

        return (
            trade_result_both,
            trade_result,
            trades_counter,
            trade_direction,
            profit_loss_long_short,
            trade_result_longs,
            trade_result_shorts
        )
    else:
        print('Trade simulation is OFF')
        return None, None, None, None, None, None, None   # Return Nones in order to avoid error when function is OFF

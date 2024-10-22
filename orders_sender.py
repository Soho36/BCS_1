from main_realtime import dataframe_from_log
import winsound

last_candle_open = dataframe_from_log['Open'].iloc[-1]
last_candle_high = dataframe_from_log['High'].iloc[-1]
last_candle_low = dataframe_from_log['Low'].iloc[-1]
last_candle_close = dataframe_from_log['Close'].iloc[-1]
ticker = dataframe_from_log['Ticker'].iloc[-1]


def send_buy_sell_orders(buy_signal, sell_signal):

    if rejection_signals_list_outside[-1] is None:
        buy_signal, sell_signal = True, True  # set Flags to True to open way to new orders
    # If there is signal and flag is False:
    if rejection_signals_list_outside[-1] == 100 and buy_signal:
        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▲ ▲ ▲ Buy signal discovered! ▲ ▲ ▲'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
        take_profit_price = round((((last_candle_close - stop_loss_price)
                                    * risk_reward) + last_candle_close) + stop_loss_offset, 3)

        line_order_parameters = f'{ticker},Buy,{stop_loss_price},{take_profit_price}'

        with open(buy_sell_signals_for_mt5_filepath, 'w', encoding='utf-8') as file:
            file.writelines(line_order_parameters)

        buy_signal = False  # Set flag to TRUE to prevent new order sending on each loop iteration
    # +------------------------------------------------------------------+
    # SELL ORDER LOGIC
    # +------------------------------------------------------------------+

    # +------------------------------------------------------------------+
    # Creating file for MT5 to read
    # +------------------------------------------------------------------+

    if rejection_signals_list_outside[-1] is None:
        buy_signal, sell_signal = True, True  # set Flags to True

    if rejection_signals_list_outside[-1] == -100 and sell_signal:  # If there is signal and flag is True:
        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▼ ▼ ▼ Sell signal discovered! ▼ ▼ ▼'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_high + stop_loss_offset)
        take_profit_price = round((last_candle_close - ((stop_loss_price - last_candle_close) *
                                                        risk_reward)) + stop_loss_offset, 3)

        line_order_parameters = f'{ticker},Sell,{stop_loss_price},{take_profit_price}'

        with open(buy_sell_signals_for_mt5_filepath, 'w', encoding='utf-8') as file:
            file.writelines(line_order_parameters)

        sell_signal = False  # Set flag to False to prevent new order sending on each loop iteration

    return buy_signal, sell_signal




time.sleep(log_file_reading_interval)  # Pause between reading
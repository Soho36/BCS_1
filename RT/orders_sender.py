import winsound
from data_handling_realtime import save_order_parameters_to_file


def last_candle_ohlc(output_df_with_levels):
    try:
        last_candle_high = output_df_with_levels['High'].iloc[-1]
        last_candle_low = output_df_with_levels['Low'].iloc[-1]
        last_candle_close = output_df_with_levels['Close'].iloc[-1]
        ticker = output_df_with_levels['Ticker'].iloc[-1]
        # print("!!!!", last_candle_high, last_candle_low, last_candle_close, ticker)
        return last_candle_high, last_candle_low, last_candle_close, ticker
    except IndexError:
        print("Must be at least two rows in the source file")
        return


def send_buy_sell_orders(
        signals_to_order_sender_series,
        buy_signal,
        sell_signal,
        last_candle_high,
        last_candle_low,
        last_candle_close,
        ticker,
        stop_loss_offset,
        risk_reward
):

    # +------------------------------------------------------------------+
    # BUY ORDER
    # +------------------------------------------------------------------+

    if signals_to_order_sender_series.iloc[-1] is None:
        buy_signal, sell_signal = True, True  # Enable new orders

    # If there is signal and flag is False:
    if signals_to_order_sender_series.iloc[-1] == 100 and buy_signal:
        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▲ ▲ ▲ Buy signal discovered! ▲ ▲ ▲'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_low - stop_loss_offset, 3)
        take_profit_price = round((((last_candle_close - stop_loss_price) * risk_reward)
                                   + last_candle_close) + stop_loss_offset, 3)

        line_order_parameters = f'{ticker},Buy,{stop_loss_price},{take_profit_price}'

        save_order_parameters_to_file(line_order_parameters)    # Located in data_handling_realtime.py

        buy_signal = False  # Set flag to TRUE to prevent new order sending on each loop iteration

    # +------------------------------------------------------------------+
    # SELL ORDER
    # +------------------------------------------------------------------+

    if signals_to_order_sender_series.iloc[-1] is None:
        buy_signal, sell_signal = True, True  # Enable new orders

    if signals_to_order_sender_series.iloc[-1] == -100 and sell_signal:  # If there is signal and flag is True:

        winsound.PlaySound('chord.wav', winsound.SND_FILENAME)
        print()
        print('▼ ▼ ▼ Sell signal discovered! ▼ ▼ ▼'.upper())

        # ORDER PARAMETERS
        stop_loss_price = round(last_candle_high + stop_loss_offset)
        take_profit_price = round((last_candle_close - ((stop_loss_price - last_candle_close) *
                                                        risk_reward)) + stop_loss_offset, 3)

        line_order_parameters = f'{ticker},Sell,{stop_loss_price},{take_profit_price}'

        save_order_parameters_to_file(line_order_parameters)    # Located in data_handling_realtime.py

        sell_signal = False  # Set flag to False to prevent new order sending on each loop iteration

    return buy_signal, sell_signal

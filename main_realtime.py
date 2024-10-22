from data_handling_realtime import get_dataframe_from_file
from orders_sender import send_buy_sell_orders
import time

# ************************************** ORDER PARAMETERS *******************************************************

volume_value = 0.01                 # 1000 MAX for stocks. Used only in AU3 (MT5 assigns volume itself)
risk_reward = 2                     # Risk/Reward ratio
stop_loss_offset = 10               # Is added to SL for Shorts and subtracted for Longs (can be equal to spread)

# **************************************************************************************************************
log_file_reading_interval = 1       # File reading interval (sec)

# GET DATAFRAME FROM LOG
dataframe_from_log = get_dataframe_from_file()


buy_signal_discovered, sell_signal_discovered = (
    send_buy_sell_orders(buy_signal_discovered, sell_signal_discovered))

time.sleep(log_file_reading_interval)   # Pause between reading







from main import (
    start_simulation,
    start_date,
    end_date,
    spread,
    filtered_by_date_dataframe,
    risk_reward_ratio,
    ticker_name
)
import statistics


def trades_analysis(
        trade_result_both,
        trade_result,
        trades_counter,
        trade_direction,
        profit_loss_long_short,
        trade_result_longs,
        trade_result_short,
        df_csv
):

    if start_simulation:

        first_row = df_csv.iloc[0]['Date']
        last_row = df_csv.iloc[-1]['Date']
        print()
        print('*****************************************************************************************')
        print('-------------------------------------TRADES ANALYSIS-------------------------------------')
        print('*****************************************************************************************')
        print(f'Ticker: {ticker_name}')
        print()
        print(f'Selected Date range: {start_date} - {end_date}'.upper(),
              f'(available period: {first_row}-{last_row})'.title()
              )
        print()

        if trades_counter == 0:
            print("No trades were placed! Try other pattern or broader date range")

        rounded_trades_list = 0
        try:
            rounded_trades_list = [round(num, 3) for num in trade_result]   # List of all trades in dollar amount
            # print(f"Trades List: {rounded_trades_list}")
        except TypeError:
            print(f'Trades List: {rounded_trades_list}')

        outcomes_string = []     # List of trade outcomes: profit or loss in order to calculate profitability %
        outcomes_positive = []      # List of positive trades

        outcomes_negative = []      # List of negative trades

        try:
            for num in rounded_trades_list:
                if num > 0:
                    outcomes_string.append('profit')
                    outcomes_positive.append(num)
                else:
                    outcomes_string.append('loss')
                    outcomes_negative.append(num)
            # print(f'Profitable trades list: {outcomes_positive}')
            # print(f'Losing trades list: {outcomes_negative}')
        except TypeError:
            print('Profitable trades list: No trades')
            print('Losing trades list: No trades')
        # Accumulate the sum of consecutive elements to illustrate balance change over time
        results_as_balance_change = []

        running_sum = 0
        try:
            running_sum = rounded_trades_list[0]
        except IndexError:
            pass

        for num in rounded_trades_list[1:]:
            running_sum += num
            results_as_balance_change.append(running_sum)

        rounded_results_as_balance_change = [round(x, 3) for x in results_as_balance_change]
        trades_count = len(outcomes_string)  # Total trades number
        profitable_trades_count = outcomes_string.count('profit')    # Profitable trades number
        losing_trades_count = outcomes_string.count('loss')    # Losing trades number

        win_percent = 0
        try:
            win_percent = (profitable_trades_count * 100) / trades_count    # Profitable trades %
        except ZeroDivisionError:
            pass

        loss_percent = 0
        try:
            loss_percent = (losing_trades_count * 100) / trades_count     # Losing trades %
        except ZeroDivisionError:
            pass
        candles_number_analyzed = len(filtered_by_date_dataframe)      # Total candles in analysis
        trades_per_candle = round(trades_count / candles_number_analyzed, 2)  # How many trades are placed in one day
        days_per_trade = 0
        try:
            days_per_trade = round(1 / trades_per_candle)      # 1 trade is placed in how many days
        except ZeroDivisionError:
            pass
        count_longs = trade_direction.count('Long')
        count_shorts = trade_direction.count('Short')
        try:
            count_profitable_longs_percent = round((profit_loss_long_short.count('LongProfit') * 100) /
                                                   count_longs, 2)
        except ZeroDivisionError:
            count_profitable_longs_percent = 0
            # print("No long trades were made")
        try:
            count_profitable_shorts_percent = round((profit_loss_long_short.count('ShortProfit') * 100) /
                                                    count_shorts, 2)
        except ZeroDivisionError:
            count_profitable_shorts_percent = 0
            # print("No short trades were made")

        # print(f'{profit_loss_long_short}')
        # print(f'List {trade_direction}')
        # print(f'Balance change over time list: {rounded_results_as_balance_change}')
        print()
        print(f'Spread: ${spread}')
        print(f'Total candles in range: {candles_number_analyzed}'.title())
        if days_per_trade > 0:
            print(f'Trades per candle: {trades_per_candle} or 1 trade every {days_per_trade} candles'.title())
        else:
            print('Trades per day: 0')
        print(f'Trades count: {trades_counter}'.title())
        print(f'Closed trades: {trades_count}'.title())
        print('**************************')
        print(f'*  risk_reward_ratio: {risk_reward_ratio}  *')
        print('**************************')
        print()
        print(f'Both trades: {sum(trade_result_both)}')
        print(f'Profitable trades: {profitable_trades_count} ({round(win_percent, 2)}%)'.title())
        print(f'Losing trades: {losing_trades_count} ({round(loss_percent, 2)}%)'.title())
        print()
        print(f'Long trades: {count_longs} ({count_profitable_longs_percent}% profitable out of all longs) '
              f'P/L: ${round(sum(trade_result_longs), 2)}'.title())
        print(f'Short trades: {count_shorts} ({count_profitable_shorts_percent}% profitable out of all shorts) '
              f'P/L: ${round(sum(trade_result_short), 2)}'.title())
        print()

        try:
            print(f'Best trade: ${max(rounded_trades_list)}'.title())
        except ValueError:
            print('Best trade: $0')

        try:
            print(f'Worst trade: ${min(rounded_trades_list)}'.title())
        except ValueError:
            print('Worst trade: $0')

        print()

        if len(outcomes_positive) > 0:
            print(f'Average profitable trade: ${round(statistics.mean(outcomes_positive), 2)}')
        else:
            print(f'Average profitable trade: No profitable trades')

        if len(outcomes_negative) > 0:
            print(f'Average losing trade: ${round(statistics.mean(outcomes_negative), 2)}')
        else:
            print(f'Average losing trade: No losing trades')

        print()
        # Calculating mathematical expectation

        # try:
        #     prob_per_trade = 1 / trades_count
        # except ZeroDivisionError:
        #     print('No closed trades')
        #
        # math_expectation = round(sum([outcome * prob_per_trade for outcome in trade_result]), 2)
        #
        # print(f'Expectation: ${math_expectation}')
        print()

        spread_loss = -1 * ((losing_trades_count * (spread * 2)) + (profitable_trades_count * spread))
        pending_order_spread_loss = -1 * (losing_trades_count * spread)

        print(f'Spread loss: ${spread_loss}'.title())
        print(f'If Pending Order spread loss : ${pending_order_spread_loss}'.title())
        print()

        p_n_l = round(sum(trade_result), 2)

        print(f'If not spread profit/loss: ${round(p_n_l - spread_loss, 2)}'.title())
        print(f'If pending order dollar per share profit/loss: ${p_n_l - pending_order_spread_loss}'.title())
        print('***************************************************************************************')
        print(f'*                       Dollar per Share profit/loss: ${p_n_l}                        *'.title())
        print('***************************************************************************************')

        return rounded_trades_list, rounded_results_as_balance_change

    else:
        print()
        return None, None    # Return Nones in order to avoid error when function is OFF

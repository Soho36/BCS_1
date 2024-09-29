import matplotlib.pyplot as plt

# BALANCE CHANGE CHART


def plot_line_chart_balance_change(
        rounded_results_as_balance_change_to_chart_profits,
        start_simulation,
        show_balance_change_line_chart,
        start_date,
        end_date,
        ticker_name
):

    if show_balance_change_line_chart and start_simulation:
        plt.figure(figsize=(10, 6))
        try:
            plt.plot(rounded_results_as_balance_change_to_chart_profits)
        except ValueError:
            print('No balance change chart to print (Trade analysis is OFF)\n')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title(f'Balance change over specified {start_date} - {end_date} date range ({ticker_name})')
        plt.grid(axis='y')


# P/L LINE CHART
def plot_line_chart_profits_losses(
        rounded_trades_list_to_chart_profits_losses,
        start_simulation,
        show_profits_losses_line_chart
):

    if show_profits_losses_line_chart and start_simulation:
        plt.figure(figsize=(10, 6))
        plt.plot(rounded_trades_list_to_chart_profits_losses)
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Trades over specified date range')
        plt.grid(axis='y')




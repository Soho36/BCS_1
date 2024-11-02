from datetime import datetime
from test2 import first_date2

# Define the path to your CSV file
path = ('C:\\Users\\Vova deduskin lap\\AppData\\Roaming\\MetaQuotes\\Terminal\\'
        'D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\hardcoded_sr_levels.csv')


def get_levels_from_file():
    with open(path, 'r', encoding='utf-8') as file:
        levels = [(first_date2, float(line.strip())) for line in file]
    return levels

# Example usage
levels = get_levels_from_file()
print(levels)

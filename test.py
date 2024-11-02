import ast

path = ('C:\\Users\\Vova deduskin lap\\AppData\\Roaming\\MetaQuotes\\Terminal\\'
        'D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\hardcoded_sr_levels.csv')


def get_levels_from_file():
    with open(path, 'r', encoding='utf-8') as file:
        # Read the entire content of the file as a single string
        content = file.read()

        # Use ast.literal_eval to safely evaluate the string as a Python literal
        levels = ast.literal_eval(content)

    return levels


# Example usage:
levels_from_file = get_levels_from_file()
print(levels_from_file)

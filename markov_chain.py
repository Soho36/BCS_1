import pandas as pd
from green_after_red import ranged_dataframe


def build_transition_matrix(df, column_name):
    """
    Build a transition matrix for candle colors.

    :param df: DataFrame containing the data.
    :param column_name: Column name representing the candle colors.
    :return: A transition matrix as a DataFrame.
    """
    # States
    states = ['G', 'R']
    transition_counts = {state: {next_state: 0 for next_state in states} for state in states}

    # Count transitions
    for i in range(len(df) - 1):
        current_state = df.iloc[i][column_name]
        next_state = df.iloc[i + 1][column_name]
        if current_state in states and next_state in states:
            transition_counts[current_state][next_state] += 1

    # Convert counts to probabilities
    trans_matrix = pd.DataFrame(transition_counts).T
    trans_matrix = trans_matrix.div(trans_matrix.sum(axis=1), axis=0)

    return trans_matrix


# Build and display the transition matrix
transition_matrix = build_transition_matrix(ranged_dataframe, 'Current_Candle_color')
print("\nTransition Matrix:")
print(transition_matrix)


def predict_next_state(current_state, transition_matrix):
    """
    Predict the next state based on the current state and transition matrix.

    :param current_state: The current state ('G' or 'R').
    :param transition_matrix: The transition matrix as a DataFrame.
    :return: The predicted next state.
    """
    probabilities = transition_matrix.loc[current_state]
    return probabilities.idxmax()  # Return the state with the highest probability


# Example prediction
current_state = ranged_dataframe.iloc[-1]['Current_Candle_color']  # Last candle's color
predicted_state = predict_next_state(current_state, transition_matrix)
print(f"Current state: {current_state}, Predicted next state: {predicted_state}")


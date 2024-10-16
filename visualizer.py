import pandas as pd
import plotly.graph_objects as go
from loader import load_data


def plot_candlestick(df):
    """
    Plot candlestick chart using Plotly.

    :param df: DataFrame containing the candlestick data
    """
    fig = go.Figure(data=[go.Candlestick(x=df['Open Time'],
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'])])
    fig.show()


def main():
    filename = input("Enter filename: ")
    df = load_data(filename)
    plot_candlestick(df)


if __name__ == "__main__":
    main()

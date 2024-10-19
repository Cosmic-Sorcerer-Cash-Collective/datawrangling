import pandas as pd
from binance.client import Client
from datetime import datetime
from alive_progress import alive_bar

client = Client()

def get_binance_klines(symbol, interval, start_date):
    """
    Fetch historical candlestick (Kline) data from Binance.

    :param symbol: Trading pair symbol, e.g., 'BTCUSDT'
    :param interval: Kline interval, e.g., '5m', '15m', '1h', etc.
    :param start_date: Start date as string or datetime object, e.g., '1 Jan 2022' or datetime object
    :return: DataFrame containing the candlestick data
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d %b %Y')

    start_timestamp = int(start_date.timestamp() * 1000)
    klines = client.get_historical_klines(symbol, interval, start_timestamp)
    columns = [
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close Time', 'Quote Asset Volume', 'Number of Trades',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
    ]
    df = pd.DataFrame(klines, columns=columns)
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
    df.drop('Ignore', axis=1, inplace=True)
    return df

def save_to_csv(df, symbol, interval):
    """
    Save DataFrame to a CSV file.

    :param df: DataFrame containing the candlestick data
    :param symbol: Trading pair symbol
    :param interval: Kline interval
    """
    filename = f'{symbol}_{interval}_candlestick_data.csv'
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    symbol = input("Enter symbol (e.g., BTCUSDT): ")
    interval = input("Enter interval (e.g., 5m, 1h, 1d): ")
    start_date = input("Enter start date (e.g., 1 Jan 2022): ")
    with alive_bar(monitor=None, stats=None, title="Fetching..."):
        df = get_binance_klines(symbol, interval, start_date)
    save_to_csv(df, symbol, interval)

if __name__ == "__main__":
    main()

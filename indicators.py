import pandas as pd
import loader

def compute_rsi(df: pd.DataFrame, periods=[14]):
    """
    Compute the Relative Strength Index (RSI) of a DataFrame.

    :param df: DataFrame containing the candlestick data
    :param period: RSI period
    :return: DataFrame with RSI values
    """
    columns = ['Open Time']
    rsiCols = [f"RSI{n}" for n in periods]
    columns.extend(rsiCols)
    res = pd.DataFrame(columns=columns)

    for period in periods:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        res['Open Time'] = df['Open Time']
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        res[f"RSI{period}"] = rsi
    return res


def compute_sma(df: pd.DataFrame, periods=[14]):
    """
    Compute the Simple Moving Average (SMA) of a DataFrame.

    :param df: DataFrame containing the candlestick data
    :param period: SMA period
    :return: DataFrame with SMA values
    """
    columns = ['Open Time', 'Close']
    smaCols = [f"SMA{n}" for n in periods]
    columns.extend(smaCols)
    res = pd.DataFrame(columns=columns)

    for period in periods:
        res['Open Time'] = df['Open Time']
        res['Close'] = df['Close']
        res[f"SMA{period}"] = df['Close'].rolling(window=period).mean()
    return res


def compute_macd(df: pd.DataFrame, shortWindow: int = 12, longWindow: int = 26, signalWindow: int = 9):
    """
    Compute the MACD, Signal Line, and MACD Histogram for a given stock price DataFrame.

    :param df: DataFrame containing at least a 'Close' price column
    :param short_window: The period for the fast EMA (default is 12)
    :param long_window: The period for the slow EMA (default is 26)
    :param signal_window: The period for the signal line (default is 9)
    :return: DataFrame with added MACD, Signal Line, and MACD Histogram columns
    """
    res = df.copy()
    res['EMA_12'] = res['Close'].ewm(span=shortWindow, adjust=False).mean()
    res['EMA_26'] = res['Close'].ewm(span=longWindow, adjust=False).mean()
    res['MACD'] = res['EMA_12'] - res['EMA_26']
    res['Signal'] = res['MACD'].ewm(span=signalWindow, adjust=False).mean()
    res['Histogram'] = res['MACD'] - res['Signal']
    return res[['Open Time', 'Close', 'MACD', 'Signal', 'Histogram']]


def compute_adx(df: pd.DataFrame, periods=[14]):
    """
    Compute the Average Directional Index (ADX) of a DataFrame.

    :param df: DataFrame containing the candlestick data
    :param period: ADX period
    :return: DataFrame with ADX values
    """
    columns = ['Open Time']
    adxCols = [f"ADX{n}" for n in periods]
    columns.extend(adxCols)
    res = pd.DataFrame(columns=columns)

    for period in periods:
        res['Open Time'] = df['Open Time']
        high = df['High']
        low = df['Low']
        close = df['Close']
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        up = high - high.shift()
        down = low.shift() - low
        plus_dm = up.where((up > down) & (up > 0), 0)
        minus_dm = down.where((down > up) & (down > 0), 0)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        res[f"ADX{period}"] = adx
    return res


def sma_scaler(df: pd.DataFrame):
    """
    Scale the SMA values to be between 0 and 1. Includes comparisons with the Close price.

    :param df: DataFrame containing the SMA values
    :return: DataFrame with scaled SMA values
    """
    res = df.copy()
    for column in df.columns:
        if column.startswith("SMA"):
            res[column] = ((df[column] - df['Close']) / df['Close']) * 100 ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res.drop(columns=['Close'], inplace=True)
    return res


def macd_scaler(df: pd.DataFrame):
    """
    Scale the MACD, Signal, and Histogram relative to the Close price without subtracting the Close price.

    :param df: DataFrame containing 'Open Time', 'Close', 'MACD', 'Signal', and 'Histogram' columns
    :return: DataFrame with scaled MACD, Signal, and Histogram values
    """
    res = df.copy()
    res['MACD_Value'] = (res['MACD'] / res['Close']) * 100 ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res['MACD_Signal'] = (res['Signal'] / res['Close']) * 100 ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res['MACD_Histogram'] = (res['Histogram'] / res['Close']) * 100 ## !!!!!!!!!!!!!!!!!!!!!!!
    res.drop(columns=['Close', 'MACD', 'Signal', 'Histogram'], inplace=True)
    return res


def combine_indicators(dfList: list, align: str = 'Open Time'):
    """
    Combine multiple indicator DataFrames into a single DataFrame. Aligns the DataFrames on the 'Open Time' column.

    :param dfList: List of DataFrames to combine
    :param align: Columns on which to align the DataFrames
    :return: DataFrame containing all indicator values
    """
    res = dfList[0]
    for df in dfList[1:]:
        res = pd.merge(res, df, on=align)
    return res


def main():
    filename = loader.prompt_file_choice()
    if filename is None:
        return
    pair = filename.split("_")[0]
    df = loader.load_data(filename)

    rsi = compute_rsi(df, periods=[7, 14, 21])
    print("RSI computed successfully.")
    rsi.dropna(inplace=True)

    adx = compute_adx(df, periods=[7, 14, 21])
    print("ADX computed successfully.")
    adx.dropna(inplace=True)

    sma = compute_sma(df, periods=[7, 14, 21])
    print("SMA computed successfully.")
    sma.dropna(inplace=True)
    scaled_sma = sma_scaler(sma)

    macd = compute_macd(df)
    print("MACD computed successfully.")
    macd.dropna(inplace=True)
    scaled_macd = macd_scaler(macd)

    """ print(rsi.head())
    print(adx.head())
    print(scaled_sma.head())
    print(scaled_macd.head()) """


    combined = combine_indicators([rsi, adx, scaled_sma, scaled_macd])
    print("Indicators combined successfully.")
    combined.to_csv(f"{pair}_indicators.csv", index=False)


if __name__ == "__main__":
    main()

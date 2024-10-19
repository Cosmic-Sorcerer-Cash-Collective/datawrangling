import loader
import json
import pandas as pd

class pcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Indicators:
    def __init__(self, timestamp: pd.Timestamp, values: dict):
        self.timestamp = timestamp
        self.values = values

    def to_json(self):
        res = "{" + f"\"timestamp\": \"{self.timestamp}\","
        for key, value in self.values.items():
            res += f"\"{key}\": {value},"
        res = res[:-1] + "}"
        return res

    def is_empty(self):
        return not bool(self.values)


class Frame:
    def __init__(self, startTime: pd.Timestamp, frameIndicatorsWindow: int, frameTargetDistance: int, frameTargetTimestamp: pd.Timestamp, indicators: list, target: int):
        self.startTime = startTime
        self.frameIndicatorsWindow = frameIndicatorsWindow
        self.frameTargetDistance = frameTargetDistance
        self.frameTargetTimestamp = frameTargetTimestamp
        self.indicators = indicators
        self.target = target

    def to_json(self):
        for indicator in self.indicators:
            if indicator.is_empty():
                return ""
        res = "{" + f"\"start\": \"{self.startTime}\","
        res += f"\"window_size\": {self.frameIndicatorsWindow},"
        res += f"\"target_distance\": {self.frameTargetDistance},"
        res += f"\"target_time\": \"{self.frameTargetTimestamp}\","
        res += "\"indicators\": ["
        for indicator in self.indicators:
            res += indicator.to_json() + ","
        res = res[:-1] + "],"
        res += f"\"target_evolution\": {self.target}"
        res += "}"
        return res


def dataframe_to_indicators(df: pd.DataFrame) -> list:
    indicators = []
    for index, row in df.iterrows():  # Unpack tuple returned by iterrows()
        timestamp = row['Open Time']  # Access 'Open Time' from the Series (row)
        values = {}
        for col in df.columns:
            if col != 'Open Time':
                values[col] = row[col]  # Access other columns similarly
        indicators.append(Indicators(timestamp, values))  # Assuming Indicators is a class that takes timestamp and values
    return indicators


def align_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, columnName: str) -> tuple:
    common = df1.merge(df2, on=columnName, how='inner')
    df1 = df1[df1[columnName].isin(common[columnName])]
    df2 = df2[df2[columnName].isin(common[columnName])]
    return df1, df2


def build_frames(dfCsticks: pd.DataFrame, dfIndicators: pd.DataFrame, frameIndicatorsWindow: int, frameTargetDistance: int) -> list:
    i = 0
    frames = []
    print(dfCsticks.head())
    print(dfIndicators.head())

    dfCsticks, dfIndicators = align_dataframes(dfCsticks, dfIndicators, 'Open Time')
    print(dfCsticks.head())
    print(dfIndicators.head())

    while i < len(dfCsticks) - frameIndicatorsWindow - frameTargetDistance + 1:
        startTime = dfCsticks.iloc[i]['Open Time']
        startPrice = dfCsticks.iloc[i]['Close']
        windowIndicators = dfIndicators.iloc[i:i + frameIndicatorsWindow]
        endPrice = dfCsticks.iloc[i + frameIndicatorsWindow + frameTargetDistance - 1]['Close']
        targetTimestamp = dfCsticks.iloc[i + frameIndicatorsWindow + frameTargetDistance - 1]['Open Time']
        target = (endPrice - startPrice) / startPrice
        indicators = dataframe_to_indicators(windowIndicators)
        frames.append(Frame(startTime, frameIndicatorsWindow, frameTargetDistance, targetTimestamp,indicators, target))
        i += 1
    return frames


def export_json_old(frames: list, filename: str):
    with open(filename, 'w') as f:
        f.write("[\n")
        for frame in frames:
            txt = frame.to_json()
            if txt:
                f.write(txt + ",\n")
            else:
                print(f"Skipping frame starting at {frame.startTime} due to missing indicator values.")
        f.write("]\n")


def export_json(frames: list, filename: str):
    with open(filename, 'w') as f:
        f.write("[\n")
        i = 0
        while i < len(frames):
            txt = frames[i].to_json()
            if txt:
                if i == len(frames) - 1:
                    f.write(txt + "\n")
                else:
                    f.write(txt + ",\n")
            else:
                print(f"Skipping frame starting at {frames[i].startTime} due to missing indicator values.")
            i += 1
        f.write("]\n")


def main():
    print(pcolors.BOLD + "JSONMAKER\n" + pcolors.ENDC)
    print("Please select the file containing the candlestick data.")
    filenameCandlestickData = loader.prompt_file_choice(headers={'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume'})
    print()
    print("Please select the file containing the corresponding indicators data.")
    filenameIndicators = loader.prompt_file_choice(headers={'Open Time', 'SMA14', 'RSI14'})
    dfCsticks = loader.load_data(filenameCandlestickData)
    dfIndicators = loader.load_data(filenameIndicators)
    frames = build_frames(dfCsticks, dfIndicators, 14, 14)
    print()
    print("Please enter the filename for the JSON output.")
    filenameJSON = input("> ")
    export_json(frames, filenameJSON)
    print()
    print(f"JSON data saved to {filenameJSON}")


if __name__ == '__main__':
    main()

import pandas as pd
import os
import csv

# Define the expected headers for a valid CSV file
REQUIRED_HEADERS = {"Open Time", "Open", "High", "Low", "Close", "Volume"}  # Example set of required headers


def load_data(filename: str) -> pd.DataFrame:
    """
    Load candlestick data from a CSV file.

    :param filename: Name of the CSV file
    :return: DataFrame containing the candlestick data
    """
    df = pd.read_csv(filename)
    # make sure the columns containing 'time' are converted into a pandas datetime
    for col in df.columns:
        if 'time' in col or 'Time' in col:
            df[col] = pd.to_datetime(df[col])
    return df


def list_csv_files() -> list:
    """Scans the current directory and returns a list of CSV files."""
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    csv_files = [file for file in files if file.endswith('.csv')]
    return csv_files


def read_csv_header(file_path: str) -> set:
    """
    Reads the header of a CSV file and returns it as a set.

    :param file_path: Path to the CSV file
    :return: Set of column names in the header
    """
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Read the first row (header)
            return set(header)  # Return the header as a set of column names
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def is_valid_csv(file_path: str, headers: set = REQUIRED_HEADERS) -> bool:
    """
    Checks if the CSV file has the required headers.

    :param file_path: Path to the CSV file
    :param headers: Set of required headers (default is REQUIRED_HEADERS)
    :return: True if the CSV file has all the required headers, False otherwise
    """
    header = read_csv_header(file_path)
    if header is None:
        return False  # Skip files with errors
    return headers.issubset(header)  # Check if required headers are present


def display_csv_files(csv_files: list):
    """
    Displays the list of CSV files with numbering.

    :param csv_files: List of CSV files to display
    :return: None
    :raises ValueError: If no files are provided
    """
    if not csv_files:
        raise ValueError("No files to display.")
    else:
        print("CSV files in the current directory:")
        for idx, file in enumerate(csv_files, start=1):
            print(f"{idx}. {file}")


def get_user_choice(csv_files: list) -> str:
    """
    Prompts the user to select a file from the list by number.

    :param csv_files (list): List of CSV files to choose from
    :return: Selected CSV file name
    :raises ValueError: If no files are provided
    """
    if not csv_files:
        raise ValueError("No files to choose from.")
    while True:
        try:
            choice = int(input("Select the file number to process (or 0 to exit): "))
            if choice == 0:
                print("Exiting.")
                return None
            elif 1 <= choice <= len(csv_files):
                return csv_files[choice - 1]
            else:
                print(f"Invalid choice. Please select a number between 1 and {len(csv_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def prompt_file_choice(headers: set = REQUIRED_HEADERS) -> str:
    """Prompts the user to select a valid CSV file from the current directory. Will select the files based on the headers provided.

    :param headers (set): The set of headers that the CSV file must contain. Default is REQUIRED_HEADERS, pass None to skip header check.

    :return str: The selected CSV file name.
    """
    csv_files = list_csv_files()
    if headers is None:
        valid_csv_files = csv_files
    else:
        valid_csv_files = [file for file in csv_files if is_valid_csv(file, headers)]
    if valid_csv_files:
        display_csv_files(valid_csv_files)
        try:
            selected_file = get_user_choice(valid_csv_files)
        except ValueError as e:
            print(e)
            return None
        if selected_file:
            print(f"You selected: {selected_file}")
            return selected_file
    else:
        print("No valid CSV files found.")

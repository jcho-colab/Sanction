import pandas as pd
import os
from typing import List, Union

class DataHandler:
    def __init__(self, base_path='data'):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def read_file(self, filename: str) -> pd.DataFrame:
        """
        Read CSV or Excel file with robust error handling
        """
        try:
            file_path = os.path.join(self.base_path, filename)
            if filename.endswith('.csv'):
                return pd.read_csv(file_path, low_memory=False)
            elif filename.endswith(('.xls', '.xlsx')):
                return pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return pd.DataFrame()

    def write_file(self, df: pd.DataFrame, filename: str):
        """
        Write DataFrame to CSV or Excel
        """
        file_path = os.path.join(self.base_path, filename)
        print(f"Writing file: {file_path}")
        try:
            if filename.endswith('.csv'):
                df.to_csv(file_path, index=False)
                print(f"Successfully wrote CSV file: {file_path}")
            elif filename.endswith(('.xls', '.xlsx')):
                df.to_excel(file_path, index=False)
                print(f"Successfully wrote Excel file: {file_path}")
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error writing file {filename}: {e}")

    def append_data(self, new_df: pd.DataFrame, filename: str):
        """
        Append new data to existing file
        """
        existing_df = self.read_file(filename)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        self.write_file(combined_df, filename)
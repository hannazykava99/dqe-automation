import os
import pandas as pd


class ParquetReader:
    def __init__(self, base_path: str = ""):
        """
        Initializes the ParquetReader.

        :param base_path: Base directory where parquet files are stored
        """
        self.base_path = base_path

    def _build_path(self, file_path: str) -> str:
        """
        Builds full file path using base_path + file_path
        """
        if self.base_path:
            return os.path.join(self.base_path, file_path)
        return file_path

    def read(self, file_path: str, columns: list = None) -> pd.DataFrame:
        """
        Reads a parquet file OR a partitioned parquet dataset (folder).

        :param file_path: Relative path to parquet file or folder
        :param columns: Optional list of columns to read
        :return: pandas DataFrame
        """
        full_path = self._build_path(file_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Parquet path not found: {full_path}")

        try:
            # This works for BOTH:
            # - single .parquet file
            # - partitioned folder dataset
            return pd.read_parquet(full_path, columns=columns)
        except Exception as e:
            raise RuntimeError(f"Failed to read parquet from {full_path}: {e}")

    def read_filtered(self, file_path: str, filters: dict) -> pd.DataFrame:
        """
        Reads parquet file and applies simple filtering.

        :param file_path: Relative path
        :param filters: dict like {"column": value}
        """
        df = self.read(file_path)

        for col, val in filters.items():
            df = df[df[col] == val]

        return df
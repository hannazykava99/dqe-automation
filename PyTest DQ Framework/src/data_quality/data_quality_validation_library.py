import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is designed to be used in a PyTest-based framework.
    Each method validates a specific data quality rule using assertions.
    """

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names=None):
        """
        Check that there are no duplicate rows in the DataFrame.
        If duplicates exist, print example rows.

        :param df: Input DataFrame
        :param column_names: Optional list of columns to check duplicates on
        """
        if df.empty:
            raise AssertionError("Cannot check duplicates on an empty DataFrame")

        if column_names:
            missing_cols = [col for col in column_names if col not in df.columns]
            assert not missing_cols, f"Columns not found in DataFrame: {missing_cols}"
            duplicates = df.duplicated(subset=column_names)
        else:
            duplicates = df.duplicated()

        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            duplicate_rows = df[duplicates]  

            # preview only
            print("\nPreview (first 7 rows):")
            print(duplicate_rows.head(7))

        assert duplicate_count == 0, f"Found {duplicate_count} duplicate rows"

    @staticmethod
    def check_count(df1: pd.DataFrame, df2: pd.DataFrame):
        """
        Check that two DataFrames have the same number of rows.

        :param df1: First DataFrame
        :param df2: Second DataFrame
        """
        assert len(df1) == len(df2), (
            f"Row count mismatch: df1={len(df1)}, df2={len(df2)}"
        )

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame):
        """
        Check that the DataFrame is not empty.

        :param df: Input DataFrame
        """
        assert df is not None, "Dataset is None"
        assert not df.empty, "Dataset is empty"

    @staticmethod
    def check_not_null_values(df: pd.DataFrame, column_names=None):
        """
        Check that specified columns (or all columns) do not contain NULL values.

        :param df: Input DataFrame
        :param column_names: Optional list of columns to validate
        """
        if df.empty:
            raise AssertionError("Cannot check NULLs on an empty DataFrame")

        if column_names:
            missing_cols = [col for col in column_names if col not in df.columns]
            assert not missing_cols, f"Columns not found in DataFrame: {missing_cols}"

            for col in column_names:
                null_count = df[col].isnull().sum()
                assert null_count == 0, f"Column '{col}' has {null_count} NULL values"
        else:
            nulls = df.isnull().sum()
            total_nulls = nulls.sum()
            assert total_nulls == 0, f"Dataset contains NULLs:\n{nulls}"

    @staticmethod
    def check_column_exists(df: pd.DataFrame, expected_columns: list):
        """
        Check that DataFrame has exactly the expected columns:
        - no missing columns
        - no unexpected columns

        :param df: Input DataFrame
        :param expected_columns: List of expected columns
        """

        actual_columns = list(df.columns)

        missing_cols = [col for col in expected_columns if col not in actual_columns]
        unexpected_cols = [col for col in actual_columns if col not in expected_columns]

        error_message = ""

        if missing_cols:
            error_message += f"\nMissing columns: {missing_cols}"

        if unexpected_cols:
            error_message += f"\nUnexpected columns: {unexpected_cols}"

        if error_message:
            error_message += f"\nActual columns: {actual_columns}"

        assert not error_message, error_message

    @staticmethod
    def check_values_in_range(df: pd.DataFrame, column: str, min_value=None, max_value=None):
        """
        Check that values in a column fall within a specified range.

        :param df: Input DataFrame
        :param column: Column name
        :param min_value: Minimum allowed value
        :param max_value: Maximum allowed value
        """
        assert column in df.columns, f"Column '{column}' not found"

        if min_value is not None:
            assert (df[column] >= min_value).all(), (
                f"Column '{column}' contains values less than {min_value}"
            )

        if max_value is not None:
            assert (df[column] <= max_value).all(), (
                f"Column '{column}' contains values greater than {max_value}"
            )

    @staticmethod
    def check_data_full_data_set(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        key_columns: list,
        compare_columns: list
    ):
        """
        Compare two DataFrames by keys and selected columns.
        Shows detailed differences.

        :param df1: First DataFrame
        :param df2: Second DataFrame
        :param key_columns: Columns to join on
        :param compare_columns: Columns to compare
        """

        # --- checks ---
        for col in key_columns + compare_columns:
            assert col in df1.columns, f"Column '{col}' missing in df1"
            assert col in df2.columns, f"Column '{col}' missing in df2"

        for col in key_columns:
            if "date" in col:
                df1[col] = pd.to_datetime(df1[col], errors="coerce")
                df2[col] = pd.to_datetime(df2[col], errors="coerce")

        # --- merge datasets ---
        merged = df1.merge(
            df2,
            on=key_columns,
            how="outer",
            suffixes=("_df1", "_df2"),
            indicator=True
        )

        # --- missing rows ---
        only_df1 = merged[merged["_merge"] == "left_only"]
        only_df2 = merged[merged["_merge"] == "right_only"]

        # --- value differences ---
        diffs = []

        for col in compare_columns:
            col_df1 = f"{col}_df1"
            col_df2 = f"{col}_df2"

            diff_rows = merged[
                (merged["_merge"] == "both") &
                (merged[col_df1] != merged[col_df2])
            ]

            if not diff_rows.empty:
                diffs.append((col, diff_rows[[*key_columns, col_df1, col_df2]].head(5)))

        # --- build error message ---
        error_message = ""

        if not only_df1.empty:
            error_message += (
                f"\n--- Rows only in df1 ---\n{only_df1[key_columns].head(5)}\n"
            )

        if not only_df2.empty:
            error_message += (
                f"\n--- Rows only in df2 ---\n{only_df2[key_columns].head(5)}\n"
            )

        for col, sample in diffs:
            error_message += (
                f"\n--- Differences in column '{col}' ---\n{sample}\n"
            )
        
        # sample.to_csv("debug_diff.csv", index=False)

        assert not error_message, f"Data mismatch detected:\n{error_message}"
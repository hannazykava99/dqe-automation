def extract_table_to_df():
    from robot.libraries.BuiltIn import BuiltIn
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import pandas as pd

    driver = BuiltIn().get_library_instance('SeleniumLibrary').driver
    wait = WebDriverWait(driver, 10)

    table = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[name()='g' and contains(@class,'table')]")
        )
    )

    columns = table.find_elements(By.CSS_SELECTOR, ".y-column")

    headers = []
    columns_data = []

    for column in columns:
        header = column.find_element(By.ID, "header").text.strip()
        headers.append(header)

        cells = column.find_elements(By.CLASS_NAME, "cell-text")

        col_data = [
            cell.text.strip()
            for cell in cells
            if cell.text.strip() and cell.text.strip() != header
        ]

        columns_data.append(col_data)

    rows = list(zip(*columns_data))
    df = pd.DataFrame(rows, columns=headers)

    df = df.rename(columns={
        "Facility Type": "facility_type",
        "Visit Date": "visit_date",
        "Average Time Spent": "avg_time_spent"
    })

    # Convert types
    df["visit_date"] = pd.to_datetime(df["visit_date"]).dt.strftime("%Y-%m-%d")
    df["avg_time_spent"] = df["avg_time_spent"].astype(float)

    # Sorting (ВАЖНО для сравнения)
    df = df.sort_values(by=["facility_type", "visit_date"]).reset_index(drop=True)

    return df


def df_to_string(df):
    return df.to_string(index=False)


def read_parquet_to_df(file_path, start_date=None, end_date=None):
    """
    Read parquet and optionally filter by visit_date
    """

    import pandas as pd

    df = pd.read_parquet(file_path)

    # --- convert to datetime ---
    df["visit_date"] = pd.to_datetime(df["visit_date"])

    # --- FILTER ---
    if start_date:
        df = df[df["visit_date"] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df["visit_date"] <= pd.to_datetime(end_date)]

    # --- select only needed columns ---
    df = df[["facility_type", "visit_date", "avg_time_spent"]]

    # --- normalize types ---
    df["visit_date"] = df["visit_date"].dt.strftime("%Y-%m-%d")
    df["avg_time_spent"] = df["avg_time_spent"].astype(float).round(2)

    # --- sort ---
    df = df.sort_values(by=["facility_type", "visit_date"]).reset_index(drop=True)

    return df


def compare_dataframes(df1, df2):
    import pandas as pd

    try:
        pd.testing.assert_frame_equal(
            df1.reset_index(drop=True),
            df2.reset_index(drop=True),
            check_dtype=False
        )
        return True, "DataFrames match"

    except AssertionError as e:
        msg = str(e) if str(e) else "DataFrames do not match (no details)"
        return False, msg
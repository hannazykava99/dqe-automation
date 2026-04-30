import os
import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


# Context manager to automatically start and close the browser
class SeleniumWebDriverContextManager:
    def __init__(self, headless=False):
        # headless = True → run browser without UI
        self.headless = headless
        self.driver = None

    def __enter__(self) -> WebDriver:
        # Create Chrome options
        options = webdriver.ChromeOptions()

        # Enable headless mode if requested
        if self.headless:
            options.add_argument("--headless=new")

        # Start Chrome browser
        self.driver = webdriver.Chrome(options=options)
        return self.driver  # return driver to use inside "with"

    def __exit__(self, exc_type, exc_value, traceback):
        # Always close the browser after execution
        if self.driver:
            self.driver.quit()


# =========================
# TASK 1: EXTRACT TABLE DATA
# =========================

def extract_table(driver, wait):

    try:
        # Wait until table container is visible (using XPATH)
        table = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[name()='g' and contains(@class,'table')]")
            )
        )

        # Find all columns using CSS selector
        columns = table.find_elements(By.CSS_SELECTOR, ".y-column")

        headers = []        # store column names
        columns_data = []   # store data for each column

        # Loop through each column
        for column in columns:

            # Get column header (using ID locator)
            header = column.find_element(By.ID, "header").text.strip()
            headers.append(header)

            # Get all cell values in this column (using CLASS_NAME)
            cells = column.find_elements(By.CLASS_NAME, "cell-text")

            # Clean cell data:
            # - remove empty values
            # - remove header duplicates if present
            col_data = [
                cell.text.strip()
                for cell in cells
                if cell.text.strip() and cell.text.strip() != header
            ]

            # Add column data to list
            columns_data.append(col_data)

        # Convert column-based data into row-based data
        rows = list(zip(*columns_data))

        # Save extracted data into CSV file
        with open("table.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(headers)   # write header row
            writer.writerows(rows)     # write data rows

        print("Data successfully saved to table.csv")

    # Handle case when table does not appear in time
    except TimeoutException:
        print("Table not found or page took too long to load")

    # Handle case when element structure is incorrect
    except NoSuchElementException:
        print("Could not locate one of the elements")

    # Catch any other unexpected errors
    except Exception as e:
        print(f"Unexpected error: {e}")


# =========================
# TASK 2: EXTRACT CHART DATA
# =========================

def extract_chart_data(driver, wait, index):
    """
    Extracts data from a Plotly doughnut/pie chart.
    
    There are 2 states:
    1. index == 0 → full chart (all segments visible)
    2. index > 0 → filtered state (tooltip for hovered slice)
    """
    try:
        time.sleep(1)  # small delay to allow UI update

        data = []

        # INITIAL STATE — extract ALL segments from full chart
        if index == 0:
            # Wait until chart SVG layer is present
            chart = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pielayer"))
            )

            # Find all text elements inside SVG (labels)
            labels = chart.find_elements(By.XPATH, ".//*[name()='text']")

            for label in labels:
                text = label.text.strip()

                # Example format: "Clinic28"
                # Split into: "Clinic" + "28"
                match = re.match(r"(.+?)(\d+)$", text)

                if match:
                    category = match.group(1).strip()
                    value = match.group(2).strip()
                    data.append([category, value])

            # Remove duplicates (SVG text often repeats)
            unique_data = []
            for row in data:
                if row not in unique_data:
                    unique_data.append(row)

            data = unique_data

        # FILTERED STATE — extract ONLY hovered slice (tooltip)
        else:
            # Tooltip container appears when hovering slice
            hover = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "hoverlayer"))
            )

            # Extract all tooltip text lines
            tspans = hover.find_elements(By.XPATH, ".//*[name()='tspan']")
            values = [t.text.strip() for t in tspans if t.text.strip()]

            print("Tooltip tspans:", values)

            # Typical tooltip format:
            # ['Clinic', '28', '36.8%']

            if len(values) >= 2:
                category = values[0]  # label
                value = values[1]     # numeric value

                data.append([category, value])

        # Edge case: no data extracted
        if not data:
            print("No data found!")
            return

        # Save extracted data to CSV
        with open(f"doughnut{index}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Facility Type", "Min Average Time Spent"])
            writer.writerows(data)

        print(f"Doughnut{index}.csv saved:", data)

    except Exception as e:
        print(f"Chart data error: {e}")


def extract_chart(driver, wait):
    """
    Main function:
    1. Captures full chart
    2. Iterates through each slice
    3. Hovers slice → captures tooltip state
    4. Saves screenshot + CSV for each state
    """
    try:
        # Wait until chart is fully loaded
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "pielayer"))
        )

        chart = driver.find_element(By.CLASS_NAME, "pielayer")

        # Scroll chart into view (important for Selenium stability)
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", chart
        )

        # Capture initial full chart state
        driver.save_screenshot("screenshot0.png")
        extract_chart_data(driver, wait, 0)

        # Find all pie/doughnut slices (SVG paths)
        slices = driver.find_elements(By.CSS_SELECTOR, "g.slice path")

        actions = ActionChains(driver)
        index = 1

        for s in slices:
            try:
                time.sleep(1)

                # Hover over slice → triggers tooltip update
                actions.move_to_element(s).perform()

                time.sleep(2)  # wait for tooltip rendering

                # Screenshot of hovered state
                driver.save_screenshot(f"screenshot{index}.png")

                # Extract tooltip data
                extract_chart_data(driver, wait, index)

                index += 1

            except Exception as e:
                print(f"Slice click error: {e}")

    except Exception as e:
        print(f"Chart error: {e}")


# =========================
# MAIN EXECUTION 
# =========================
if __name__ == "__main__":
    # Use context manager to handle browser lifecycle
    with SeleniumWebDriverContextManager(headless=False) as driver:

        # Build path to local HTML file
        file_path = f"file:///{os.path.abspath('report.html')}"
        driver.get(file_path)

        # Create wait object (max 15 seconds)
        wait = WebDriverWait(driver, 15)

        try:
            # Run table extraction
            extract_table(driver, wait)

            # Run chart extraction
            extract_chart(driver, wait)

        except TimeoutException:
            print("Page took too long to load")

        except Exception as e:
            print(f"Unexpected error: {e}")
DESCRIPTION
Automates extraction of table and chart data from an HTML report using Selenium. Saves results as CSV files and captures screenshots.

FEATURES
- Extracts SVG-based table data
- Extracts doughnut/pie chart data
- Supports hover tooltip scraping
- Saves screenshots for each state
- Handles errors and timeouts

OUTPUT FILES
- table.csv (table data)
- doughnut0.csv, doughnut1.csv... (chart data)
- screenshot0.png, screenshot1.png... (chart states)

HOW IT WORKS
1. Opens HTML report in Chrome via Selenium
2. Extracts table columns and converts them into rows
3. Captures full chart data from SVG labels
4. Hovers each pie slice to get tooltip data
5. Saves all results into CSV + screenshots

REQUIREMENTS
- Python 3+
- Selenium
- Chrome + ChromeDriver

RUN
python main.py

NOTE
Works with SVG-based charts (e.g., Plotly). Uses hover actions to trigger tooltips.
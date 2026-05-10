*** Settings ***
Library    SeleniumLibrary
Library    helper.py

Suite Teardown    Close Browser


*** Variables ***
${REPORT_FILE}      report.html
${PARQUET_FOLDER}   parquet_data/facility_type_avg_time_spent_per_visit_date
${START_DATE}     2026-03-16
${END_DATE}       2026-03-22


*** Test Cases ***
Compare UI vs Parquet

    # --- Open HTML report ---
    ${URL}=    Evaluate    "file:///" + __import__('os').path.abspath('${REPORT_FILE}')
    Open Browser    ${URL}    chrome
    Sleep    2s

    # --- Extract table from UI ---
    ${ui_df}=    Extract Table To DF

    ${ui_str}=    DF To String    ${ui_df}
    Log    <b>=== UI DATA ===</b>    html=True
    Log    <pre>${ui_str}</pre>    html=True

    # --- Read parquet (with filtering) ---
    ${pq_df}=    Read Parquet To DF    ${PARQUET_FOLDER}    ${START_DATE}    ${END_DATE}

    ${pq_str}=    DF To String    ${pq_df}
    Log    <b>=== PARQUET DATA ===</b>    html=True
    Log    <pre>${pq_str}</pre>    html=True

    # --- Compare ---
    ${status}    ${result}=    Compare Dataframes    ${ui_df}    ${pq_df}
    Run Keyword If    not ${status}    Fail    Mismatch found:\n${result}

    Log    ✅ DataFrames match
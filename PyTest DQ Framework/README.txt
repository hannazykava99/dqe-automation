# Data Quality Automation Framework

PyTest-based framework for validating PostgreSQL tables and Parquet data.

---

## Features

- DB table validation (facilities, patients, visits)
- Parquet validation
- DB vs Parquet comparison
- Duplicates, NULLs, schema checks
- HTML test report

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

 
# Run tests


pytest -v -s --html=report_example.html --self-contained-html \
--db_host="localhost" \
--db_port=5434 \
--db_name="mydatabase" \
--db_user="" \      # insert user name
--db_password=""    # insert password
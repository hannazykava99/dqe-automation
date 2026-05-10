# UI vs Parquet Check

## What it does

* Opens HTML report
* Reads table data
* Reads Parquet data
* Compares both

---

## Run test

```bash
robot --outputdir ./results test.robot
```

---

## Results

After run:

```
results/
├── log.html
├── report.html
├── output.xml
```

Open:

```bash
open results/log.html
```

---

## Notes

* Data is compared as DataFrames
* Dates are normalized
* Test fails if data is different

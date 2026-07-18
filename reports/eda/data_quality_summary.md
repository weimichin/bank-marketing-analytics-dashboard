# Data Quality Assessment Summary Report

## Observation
- Quality checks use the cleaned dataset with 41176 rows and 21 columns.
- Exact-duplicate rows to remove before cleaning: 12; after cleaning: 0.
- NaN/None missing values across all columns total 0.
- Categorical `unknown` labels remain present; highest rate is in `default`.

## Key Statistics
- Duplicate rows before cleaning: 12 (rate=0.000291).
- Duplicate rows after cleaning: 0 (rate=0.000000).
- Missing values: all columns have missing_count=0.
- Unknown rates (top): default=0.2088, education=0.0420, housing=0.0240.
- pdays sentinel (999): 39661; previously contacted: 1515.

## Notable Patterns
- Highest IQR outlier rate among numeric columns: `previous` (0.1366).
- Logical consistency checks with non-zero counts: pdays==999 but previous>0=4110, duration==0=4.
- Outlier boxplots saved under images/data_quality for age, duration, campaign, and previous.
- Rows removed by exact-duplicate cleaning: 12.

# Data Overview Summary Report

## Observation
- Cleaned dataset shape is 41176 rows and 21 columns.
- There are 10 numeric columns and 11 categorical columns.
- Feature groups present: Demographics, Financial Features, Marketing Behavior, Time Analysis, Macroeconomic Context.
- Target column is `y`.

## Key Statistics
- Row count: 41176; column count: 21.
- Memory usage (deep): 26.80 MB.
- Dtype counts: str=11, int64=5, float64=5.
- Numeric columns: age, duration, campaign, pdays, previous, emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed.
- Categorical columns: job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome, y.

## Notable Patterns
- All configured feature groups are present in the cleaned dataset.
- Head and tail previews show records spanning early and late campaign periods in the file order.
- Index is reset after exact-duplicate removal (range index 0 to 41175).

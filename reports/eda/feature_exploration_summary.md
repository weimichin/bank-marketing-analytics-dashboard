# Feature Exploration Summary Report

## Observation
- Feature exploration uses the cleaned dataset with 41176 rows.
- Explored groups: Demographics, Financial Features, Marketing Behavior, Time Analysis, Macroeconomic Context.
- Age mean is 40.02 and median is 38.0.
- Most frequent job category is `admin.` (25.30% of rows).

## Key Statistics
- Job subscription rate range: blue-collar=0.0690 to student=0.3143.
- poutcome rates: success=0.6511 (n=1373), failure=0.1423 (n=4252), nonexistent=0.0883 (n=35551).
- contact rates: cellular=0.1474 (n=26135), telephone=0.0523 (n=15041).
- Highest-volume month: may (n=13767); highest subscription-rate month: mar (rate=0.5055).
- Previously contacted share (pdays != 999): 0.0368.

## Notable Patterns
- Duration mean by target: no=220.9, yes=553.3.
- Mean euribor3m by target: no=3.811, yes=2.123.
- Mean nr.employed by target: no=5176.2, yes=5095.1.
- Figures are saved under images/feature_exploration for all five feature groups.

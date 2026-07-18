# Bias & Limitation Checks Summary Report

## Observation
- Bias and limitation checks use the cleaned dataset with 41176 rows.
- Target class proportions: no=0.8873, yes=0.1127.
- Duration has correlation 0.4053 with y_binary; duration==0 rows: 4.
- Dataset documentation notes duration is known only after the call.

## Key Statistics
- Unknown label highest rate: default=0.2088 (count=8596).
- pdays sentinel rate: 0.9632; previously contacted share: 0.0368.
- Highest-volume month: may (share=0.3343).
- Dominant contact channel: cellular (share=0.6347).
- Macro unique combinations: 375; mean rows per combination: 109.8.

## Notable Patterns
- Duration decile subscription rates range from 0.0002 to 0.4603.
- Positive outcomes (y=yes): 4639 of 41176.
- Demographic categories with count < 100: marital=unknown (n=80, rate=0.1500), education=illiterate (n=18, rate=0.2222).
- Figures are saved under images/bias_limitation.

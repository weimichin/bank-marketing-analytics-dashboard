# Executive Summary

## Project Objective
- This project analyzes the Bank Marketing dataset to understand which factors are associated with term deposit subscription. The cleaned dataset contains 41,176 observations after removing 12 exact duplicate rows, with an overall subscription rate of 11.27%.
- The analysis is descriptive and business-oriented. It does not build predictive models, estimate causal effects, or introduce new scoring rules.
- The project answers three business questions:
  - Which customer characteristics are associated with higher term deposit subscription rates?
  - Which telephone marketing strategies and historical campaign characteristics are associated with higher subscription rates?
  - Are macroeconomic conditions associated with subscription outcomes, and should market environment be considered when planning telephone marketing strategy?

## Key Findings

### 1. Customer Targeting
- Customer characteristics show observable differences in subscription rates, with `job` showing the widest variation across categories. `loan` shows the narrowest variation, suggesting limited differentiation by personal loan status alone.
- Higher-potential customer-profile signals come from combining conversion rate, group size, contribution to subscribers, and quadrant placement. Examples of higher-potential or high-impact segments include students, retired customers, single customers, and customers with university degrees.
- Some large groups contribute heavily to total subscribers even when their conversion rate is not the highest. For example, `admin.` and `married` are important because of their scale.
- Age differences are modest: subscribers are only about one year older on average than non-subscribers, so age should not be treated as a primary targeting factor by itself.
- Small-sample categories such as `marital=unknown`, `education=illiterate`, and `default=yes` should be interpreted cautiously and should not drive business decisions on their own.

### 2. Campaign Strategy
- Contact method is strongly associated with observed subscription rates: `cellular` contacts have a higher subscription rate than `telephone` contacts.
- Lower contact frequency is associated with better observed outcomes. Customers contacted once show the highest subscription rate, while customers contacted `6+` times show the lowest rate.
- Prior campaign engagement is one of the strongest campaign-related signals. Customers with `previous >= 1`, `pdays != 999`, and especially `poutcome = success` show substantially higher observed subscription rates than customers with no prior campaign contact.
- Timing matters, but should be interpreted with volume. March has the highest subscription rate, while May has the largest campaign volume but the lowest subscription rate. Weekday differences are comparatively modest and should not be used as a primary rule.
- These findings are associations only. Prior success, previous contact, or cellular contact should not be interpreted as causing subscription without further controlled analysis.

### 3. Macroeconomic Environment
- Macroeconomic conditions show an observable statistical association with subscription outcomes. The strongest macro-related association is with `nr.employed`, followed by `euribor3m` and `emp.var.rate`.
- `cons.price.idx` has a weaker association with subscription, and `cons.conf.idx` is the weakest macro indicator in this module.
- The bank should consider market environment as context when evaluating telephone marketing performance, especially when comparing results across months or market conditions.
- Macroeconomic indicators should not be used as the only decision basis. Several indicators are highly correlated with each other, and macro variables are closely tied to `month`.
- The analysis does not support causal claims. It shows that market conditions and subscription rates moved together during this campaign period, not that macroeconomic changes directly caused subscription behavior.

## Business Recommendations
- Combine customer-profile, campaign, and market-context findings when planning campaigns. Customer targeting should not rely on a single variable such as age, loan status, or one high-rate category.
- Prioritize campaign review around contact channel and contact frequency. The observed results support reviewing the use of `cellular` contact and avoiding excessive repeated contacts where possible.
- Use prior engagement as a practical follow-up signal. Customers with previous positive campaign outcomes or recent prior contact appear meaningfully different, but this should be used as a prioritization guide rather than a predictive score.
- Balance conversion rate with customer volume. High conversion alone should not determine targeting priorities because small segments may contribute relatively few subscribers.
- Include macroeconomic context in performance evaluation. Month-to-month campaign results should be assessed alongside market indicators, while clearly separating correlation from causation.

## Limitations
- The project is based on observational data. The analysis identifies associations, not causal effects.
- The target class is imbalanced: only 11.27% of observations subscribed, so rates and segment comparisons should be interpreted with class imbalance in mind.
- Some categories or subgroups have relatively small sample sizes, so their observed conversion rates should be interpreted cautiously.
- Campaign variables such as `previous`, `pdays`, and `poutcome` are highly imbalanced; most customers had no prior campaign contact.
- Macroeconomic variables are closely tied to `month`, and several macro indicators are highly correlated with each other. This limits the ability to isolate the independent effect of any single macro variable.

# Interaction Analysis Summary Report

## Observation
- Interaction analysis uses the cleaned dataset with 41176 rows.
- Analyses include numeric-target correlations, numeric feature correlations, and categorical pair subscription rates.
- Two-way heatmaps and scatter plots are saved under images/interaction_analysis.
- Strongest absolute correlation with target among numeric features is `duration` (0.4053).

## Key Statistics
- Numeric correlations with y_binary (top 5 by absolute value): duration=0.4053, nr.employed=-0.3547, pdays=-0.3249, euribor3m=-0.3077, emp.var.rate=-0.2983.
- Strongest absolute numeric feature pair correlation: emp.var.rate vs euribor3m (0.9722).
- Highest job x marital subscription rate in top-20 table: entrepreneur / unknown (rate=0.3333, n=3).
- Highest contact x poutcome subscription rate: cellular / success (rate=0.6520, n=1270).
- Month with highest mean subscription rate: mar (rate=0.5055).

## Notable Patterns
- Monthly mean euribor3m for highest-rate month (mar): 1.163.
- Monthly mean nr.employed for highest-rate month (mar): 5055.4.
- Lowest monthly mean subscription rate: may (0.0644).
- Cross-group tables include job x contact and age_bin x poutcome subscription rates.

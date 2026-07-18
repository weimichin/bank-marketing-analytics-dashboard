# **Data Overview Summary Report**

## **Observation**

* Cleaned dataset shape is 41176 rows and 21 columns.  
* There are 10 numeric columns and 11 categorical columns.  
* Feature groups present: Demographics, Financial Features, Marketing Behavior, Time Analysis, Macroeconomic Context.  
* Target column is y.

## **Key Statistics**

* Row count: 41176; column count: 21\.  
* Memory usage (deep): 26.80 MB.  
* Dtype counts: str=11, int64=5, float64=5.  
* Numeric columns: age, duration, campaign, pdays, previous, emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed.  
* Categorical columns: job, marital, education, default, housing, loan, contact, month, day\_of\_week, poutcome, y.

## **Notable Patterns**

* All configured feature groups are present in the cleaned dataset.  
* Head and tail previews show records spanning early and late campaign periods in the file order.  
* Index is reset after exact-duplicate removal (range index 0 to 41175).

# 

# **Data Quality Assessment Summary Report**

## **Observation**

* Quality checks use the cleaned dataset with 41176 rows and 21 columns.  
* Exact-duplicate rows to remove before cleaning: 12; after cleaning: 0\.  
* NaN/None missing values across all columns total 0\.  
* Categorical unknown labels remain present; highest rate is in default.

## **Key Statistics**

* Duplicate rows before cleaning: 12 (rate=0.000291).  
* Duplicate rows after cleaning: 0 (rate=0.000000).  
* Missing values: all columns have missing\_count=0.  
* Unknown rates (top): default=0.2088, education=0.0420, housing=0.0240.  
* pdays sentinel (999): 39661; previously contacted: 1515\.

## **Notable Patterns**

* Highest IQR outlier rate among numeric columns: previous (0.1366).  
* Logical consistency checks with non-zero counts: pdays999 but previous\>0=4110, duration0=4.  
* Outlier boxplots saved under images/data\_quality for age, duration, campaign, and previous.  
* Rows removed by exact-duplicate cleaning: 12\.

# 

# **Target Distribution Summary Report**

## **Observation**

* Target analysis uses the cleaned dataset with 41176 rows.  
* Target column y has two classes: yes and no.  
* Class no accounts for 36537 rows; class yes accounts for 4639 rows.  
* Count and pie charts are saved under images/target\_distribution.

## **Key Statistics**

* y=no: count=36537, proportion=0.8873.  
* y=yes: count=4639, proportion=0.1127.  
* Majority class: no (36537).  
* Minority class: yes (4639).  
* Imbalance ratio (majority/minority): 7.876; minority rate: 0.1127.

## **Notable Patterns**

* The majority class is no and the minority class is yes.  
* Minority class share is 11.27% of all cleaned rows.  
* Majority class is approximately 7.88 times the minority class count.

# 

# **Feature Exploration Summary Report**

## **Observation**

* Feature exploration uses the cleaned dataset with 41176 rows.  
* Explored groups: Demographics, Financial Features, Marketing Behavior, Time Analysis, Macroeconomic Context.  
* Age mean is 40.02 and median is 38.0.  
* Most frequent job category is admin. (25.30% of rows).

## **Key Statistics**

* Job subscription rate range: blue-collar=0.0690 to student=0.3143.  
* poutcome rates: success=0.6511 (n=1373), failure=0.1423 (n=4252), nonexistent=0.0883 (n=35551).  
* contact rates: cellular=0.1474 (n=26135), telephone=0.0523 (n=15041).  
* Highest-volume month: may (n=13767); highest subscription-rate month: mar (rate=0.5055).  
* Previously contacted share (pdays \!= 999): 0.0368.

## **Notable Patterns**

* Duration mean by target: no=220.9, yes=553.3.  
* Mean euribor3m by target: no=3.811, yes=2.123.  
* Mean nr.employed by target: no=5176.2, yes=5095.1.  
* Figures are saved under images/feature\_exploration for all five feature groups.

# 

# **Interaction Analysis Summary Report**

## **Observation**

* Interaction analysis uses the cleaned dataset with 41176 rows.  
* Analyses include numeric-target correlations, numeric feature correlations, and categorical pair subscription rates.  
* Two-way heatmaps and scatter plots are saved under images/interaction\_analysis.  
* Strongest absolute correlation with target among numeric features is duration (0.4053).

## **Key Statistics**

* Numeric correlations with y\_binary (top 5 by absolute value): duration=0.4053, nr.employed=-0.3547, pdays=-0.3249, euribor3m=-0.3077, emp.var.rate=-0.2983.  
* Strongest absolute numeric feature pair correlation: emp.var.rate vs euribor3m (0.9722).  
* Highest job x marital subscription rate in top-20 table: entrepreneur / unknown (rate=0.3333, n=3).  
* Highest contact x poutcome subscription rate: cellular / success (rate=0.6520, n=1270).  
* Month with highest mean subscription rate: mar (rate=0.5055).

## **Notable Patterns**

* Monthly mean euribor3m for highest-rate month (mar): 1.163.  
* Monthly mean nr.employed for highest-rate month (mar): 5055.4.  
* Lowest monthly mean subscription rate: may (0.0644).  
* Cross-group tables include job x contact and age\_bin x poutcome subscription rates.

# 

# **Bias & Limitation Checks Summary Report**

## **Observation**

* Bias and limitation checks use the cleaned dataset with 41176 rows.  
* Target class proportions: no=0.8873, yes=0.1127.  
* Duration has correlation 0.4053 with y\_binary; duration==0 rows: 4\.  
* Dataset documentation notes duration is known only after the call.

## **Key Statistics**

* Unknown label highest rate: default=0.2088 (count=8596).  
* pdays sentinel rate: 0.9632; previously contacted share: 0.0368.  
* Highest-volume month: may (share=0.3343).  
* Dominant contact channel: cellular (share=0.6347).  
* Macro unique combinations: 375; mean rows per combination: 109.8.

## **Notable Patterns**

* Duration decile subscription rates range from 0.0002 to 0.4603.  
* Positive outcomes (y=yes): 4639 of 41176\.  
* Demographic categories with count \< 100: marital=unknown (n=80, rate=0.1500), education=illiterate (n=18, rate=0.2222).  
* Figures are saved under images/bias\_limitation.
These notes are preliminary observations recorded during EDA. They are intended to highlight data characteristics and potential limitations, rather than draw business conclusions or infer causality.


A. Features Requiring Cautious Interpretation

Campaign

* 存在極端離群值（平均約 2.56，最大值 56）。
* yes 與 no 的平均聯絡次數接近，是否具有鑑別能力需進一步評估。

Duration

* 存在極端離群值（最大約 4000 多秒）。
* 此欄位僅能於通話結束後取得，若建立預測模型需留意資料洩漏（data leakage）風險。
* 通話時間較長不代表一定成交，不宜單獨解讀。

Age

* yes 與 no 的平均年齡相近，平均值未呈現明顯差異。

Marital

* unknown 類別樣本數最少，但轉換率最高。
* 各婚姻狀態之間的轉換率差異整體有限。

Housing

* 三個類別的轉換率約落在 10.8%–11.6%，整體差異有限。

Loan

* 三個類別的轉換率約落在 10.8%–11.3%，整體差異有限。

Housing × Loan

* 各組轉換率差異有限，是否具有額外分析價值需進一步評估。

Default × Housing

* 各組轉換率差異有限，是否具有額外分析價值需進一步評估。

Day of Week

* 各星期的成交比例分布相近，未觀察到明顯差異。

Contact × Poutcome

* 交叉結果主要受到 poutcome 分布影響，解讀時需留意其影響。

Age Bins × Poutcome

* 不同年齡區間的結果仍主要受 poutcome 影響。

Consumer Price Index

* yes 與 no 的平均值接近。

Consumer Confidence Index

* yes 與 no 的平均值接近。

Time × Macro Indicators

* Macro 指標與月份具有高度對應關係，需評估是否提供額外資訊。

⸻

B. Sample Imbalance / Data Limitation

Previous

* 過去聯絡次數平均接近 0。
* 曾聯絡過的客戶比例較低。

Pdays

* 約 96% 客戶屬於 999（未曾聯絡）。
* 曾聯絡過樣本約 1,515 筆，轉換率較高（約 63.8%）。
* 解讀時需考慮樣本分布不均。

Poutcome

* success 約占整體 3.3%，但轉換率約 65%。
* 樣本比例偏低，解讀時需留意。

Target (y)

* yes 約占整體 11%，存在類別不平衡（class imbalance）。

Job

* student 轉換率最高，但樣本約占 2%。
* retired 次高，樣本約占 4%。
* 高轉換率可能受樣本數影響，需審慎解讀。

Education

* illiterate 樣本僅約 18 筆。
* unknown 約 1,731 筆。
* 樣本數差異較大，高轉換率需搭配樣本量一起評估。

Month

* mar、sep、oct、dec 的轉換率較高，但樣本比例均偏低（約 0.4%–1.7%）。
* 不宜僅依轉換率判斷月份效果。

Job × Marital

* 高轉換率組合多來自樣本數較少的組別。
* 解讀時應同時考量樣本量。

Education × Marital

* 高轉換率組合多數樣本有限，需審慎解讀。










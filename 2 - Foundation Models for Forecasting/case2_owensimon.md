# Case 2 — Owen Simon

Choice record: On October 5, 2026, after seeing the validation table,
I chose TimesFM because it had the lowest validation MAE.

## Q1 — Run it and describe the methods

### 1a Output

```
(vd2) C:\Users\owens\Repositories\TG-MKTG-6620\2 - Foundation Models for Forecasting>python VD2_analysis.py compare --csv data/train.csv --out outputs
        method  rows  stores         mae     wape  absolute_error_sum  actual_sum
seasonal_naive  1680      20 1429.518452 0.209521        2.401591e+06  11462287.0
  weekday_mean  1680      20 1243.255432 0.182221        2.088669e+06  11462287.0
       timesfm  1680      20 1198.039075 0.175594        2.012706e+06  11462287.0
Record your choice and reason before using evaluate. Lower MAE is better.

(vd2) C:\Users\owens\Repositories\TG-MKTG-6620\2 - Foundation Models for Forecasting>python VD2_analysis.py evaluate --csv data/train.csv --out outputs --choice timesfm
        method  rows  stores         mae     wape  absolute_error_sum  actual_sum
seasonal_naive   840      20 1208.002381 0.174225        1.014722e+06   5824198.0
  weekday_mean   840      20 1163.402381 0.167793        9.772580e+05   5824198.0
       timesfm   840      20 1161.340174 0.167495        9.755257e+05   5824198.0
Recorded choice: timesfm Keep it visible if the final ordering changes.
```

### 1b Methods

- **Seasonal naive**: The seasonal naive method uses the last complete week of training data and repeats it to forecast the next 42 days.
- **Weekday mean**: The weekday mean method uses the last 56 training days, including observed zero-sales days, to calculate seven averages, one for each day of the week.
- **TimesFM**: TimesFM uses the last 84 observed days of training data to forecast the next 42 days.
   - *The TimesFM forecasts were supplied to me rather than generated or fitted by me.*


### 1c AI use, commands, and versions

I used AI to help troubleshoot my Python environment and clarify the assignment instructions. I checked and understood that TimesFM had the lowest validation MAE of 1198.04 and that it also had the lowest final MAE of 1161.34. 

I ran the following using Python 3.11.17, pandas 2.0.0, and NumPy 1.24.2.

```
python VD2_analysis.py compare --csv data/train.csv --out outputs 
python VD2_analysis.py evaluate --csv data/train.csv --out outputs --choice timesfm 
```

## Q2 — Is the test fair, and how accurate is each method?

### 2a Data

The final window included 20 stores and 840 store-days for each method. The agent confirmed that there were no repeated store-dates or missing forecasts. The `Customers` column was excluded because it represents a contemporaneous count; customer count for a future day would not be known when the forecast is made, so using it would introduce future information.

### 2b Fair test

You cannot test on randomly chosen days because you could accidentally train the forecasting method on data from a day that occurred after a test day. That would allow information from the future to influence an earlier forecast.

The agent ran a no-peeking check on store 1. The seasonal naive forecast for June 27 was 4256, which equals its actual sales on June 13 (4256) rather than its actual sales on June 20 (4097). This is correct because June 13 was part of the training data available before the forecast window began, while June 20 was inside the forecast window. Using June 20 sales would mean the forecast was using future information that would not have been available when the forecast was made.

The script sets the forecast to zero on days the store was closed under the assumption that the retailer knows whether each store will be open or closed for every day in the six-week forecast period. This assumption is somewhat realistic, as retailers often plan closures in advance. However, the assumption may not always hold if a store has an unexpected closure.

### 2c Accuracy

| Method | Final MAE | Final WAPE |
|:--|:--:|:--:|
| Seasonal naive | 1208.00 | 0.1742 |
| Weekday mean | 1163.40 | 0.1678 |
| TimesFM | 1161.34 | 0.1675 |

**MAE** measures the average absolute difference between actual sales and forecasted sales per store-day.

$$
\text{WAPE}_{\text{TimesFM}}
= \frac{975{,}525.746459961}{5{,}824{,}198}
= 0.1674952923
$$

- **Numerator** (`absolute_error_sum`): The total absolute error between actual and forecasted sales across the 840 store-days in the final window.
- **Denominator** (`actual_sum`): The total actual sales across those same 840 store-days in the final window.

## Q3 — How sure are we, and does the result hold up?

### 3a Uncertainty

| Comparison | MAE Difference | 95% CI | Includes 0? |
|---|---:|---:|---|
| TimesFM − weekday mean | -2.06 | [-59.26, 77.64] | Yes |
| TimesFM − seasonal naive | -46.66 | [-157.20, 79.58] | Yes |

Both comparisons favor TimesFM, becuase it had a lower MAE than weekday mean by 2.06 and seasonal naive by 46.66. However, both 95% intervals include zero, so the results do not provide clear evidence that TimesFM has lower MAE than either weekday mean or seasonal naive.

The script resamples stores rather than individual days because the 42 daily observations within each store may be related, so resampling stores keeps each store's daily observations together. These intervals do not account for uncertainty across different future time periods.

### 3b Does the ranking hold?

| Evaluation | Stores | Seasonal naive | Weekday mean | TimesFM | Lowest MAE |
|:--|:--:|:--:|:--:|:--:|:--|
| Validation A | 20 | 1763.56 | **1368.75** | 1369.06 | Weekday mean |
| Validation B | 20 | 1095.47 | 1117.76 | **1027.02** | TimesFM |
| Final window | 20 | 1208.00 | 1163.40 | **1161.34** | TimesFM |
| Sunday-trading | 5 | **1324.15** | 1500.38 | 1582.48 | Seasonal naive |
| Other stores | 15 | 1169.29 | 1051.08 | **1020.96** | TimesFM |

The order and size of the gaps do not stay the same. Weekday mean had the lowest MAE in Validation A, TimesFM had the lowest MAE in Validation B and the final window, and seasonal naive had the lowest MAE among the Sunday-trading stores. The differences also varied in size, with TimesFM and weekday mean separated by only 0.31 in Validation A, compared to 90.74 in Validation B.

These results are based on only 20 stores and three forecast windows, so they do not show that the same method would perform best for every store or in a future forecast window. The analysis also measures sales forecast accuracy rather than staffing outcomes, so it cannot show that a more accurate sales forecast would necessarily lead to better staffing decisions.

### 3c The closed-day adjustment

| Method | Raw MAE | Known-schedule MAE | Change |
|:--|:--:|:--:|:--:|
| Seasonal naive | 1208.00 | 1208.00 | 0.00 |
| Weekday mean | 1163.40 | 1163.40 | 0.00 |
| TimesFM | 1198.02 | 1161.34 | -36.68 |

The known-schedule adjustment did not affect seasonal naive or weekday mean because both methods already forecasted zero sales on all closed days. However, TimesFM had nonzero forecasts on 45 closed store-days, so setting those forecasts to zero reduced its MAE by 36.68. If the store schedule was not known in advance, I would trust the raw MAE of 1198.02 because it measures the forecasts before using future store-closure information.

### 3d TimesFM's forecast range

| Universe | Rows | Covered rows | Coverage | Average interval width (`q90 − q10`) |
|:---|:--:|:--:|:--:|:--:|
| All days | 840 | 765 | 0.9107 (91.07%) | 4888.34 |
| Open days only | 750 | 675 | 0.9000 (90.00%) | 5474.94 |

Actual sales fell within TimesFM's q10-q90 range on 765 of the 840 store-days, for 91.07% coverage, and on 675 of the 750 open store-days, for 90.00% coverage. Open days are reported separately because all 90 closed store-days had actual sales, q10, and q90 equal to zero, so they were automatically covered, which increased the overall coverage from 90.00% to 91.07%.

Coverage above the intended 80% is not automatically good news because wider forecast ranges make it easier to capture actual sales. TimesFM's average interval width was 4,888.34 sales across all days and 5,474.94 sales on open days, so the high coverage needs to be considered along with the width of the range.

The q10-q90 forecast range represents uncertainty about actual future sales, while the interval in 3a represents uncertainty about the difference in MAE between forecasting methods.

## Q4 — Your choice and what would change it

### 4a Choice record

Choice record: On October 5, 2026, after seeing the validation table,
I chose TimesFM because it had the lowest validation MAE.

### 4b Comparison table

| Method | Validation MAE | Final MAE | Final WAPE | Role | Reason (one sentence) |
|:--|:--:|:--:|:--:|:--:|:--|
| Seasonal naive | 1429.52 | 1208.00 | 0.1742 | Benchmark | It provides a simple baseline for determining whether the more advanced methods actually improve forecast accuracy. |
| Weekday mean | 1243.26 | 1163.40 | 0.1678 | Operational choice | Its final MAE and WAPE were nearly identical to TimesFM, and its performance did not depend on the known-schedule adjustment. |
| TimesFM | 1198.04 | 1161.34 | 0.1675 | Pilot candidate | It had the lowest validation and adjusted final MAE, but its advantage over weekday mean was small, not statistically significant and partially depended on the known-schedule adjustment. |

### 4c What would change my recommendation

A further test that could change my recommendation would be evaluating TimesFM and weekday mean on another six-week forecast window using raw forecasts. If TimesFM had a meaningfully lower raw MAE than weekday mean and the 95% interval for the MAE difference did not include zero, I would consider changing the operational choice to TimesFM.

## Q5 — Memo to Rina Kapoor
(at most about 400 words)

## AI record
(your prompts and the key parts of the AI's replies,
including anything that didn't work)

### Prompt 1:

> Help me gather and verify the information needed for Q2 of the assignment using the provided files and outputs. Do not write my assignment responses or modify any files. For Q2a, use `outputs/final_predictions.csv` to report the number of unique stores and store-days for each forecasting method, confirm whether any store-date combination appears more than once within a method, and confirm whether any forecast values are missing. Also inspect `VD2_analysis.py` and identify why the `Customers` column is excluded. For Q2b, perform the no-peeking check for store 1 by reporting its seasonal naive forecast for June 27, 2015 from `outputs/final_predictions.csv`, its actual sales on June 13, 2015 from `data/train.csv`, and its actual sales on June 20, 2015. State which actual value the June 27 forecast matches and identify the relevant code logic. Also inspect how the script sets forecasts to zero on closed days and explain mechanically how this known-schedule adjustment works. Provide these results and checks only so I can write the explanations in my own words.

**Key parts of Codex's reply:**

- Each method (`seasonal_naive`, `weekday_mean`, and `timesfm`) contains 20 unique stores and 840 unique store-days.
- No store-date combination appears more than once within a method, and there are no missing point forecast values.
- `Customers` is not used as a predictor. The baseline forecasts are constructed from historical `Sales`, and customer counts for the forecasted day would not be a known future input.
- For store 1:
  - June 27 seasonal-naive forecast = **4,256**
  - June 13 actual sales = **4,256**
  - June 20 actual sales = **4,097**
- The June 27 forecast therefore matches June 13, not June 20. The script uses the historical observations available before the June 20 forecast origin and repeats the final seven historical sales values across the forecast horizon.
- The known-schedule adjustment multiplies each forecast by `Open`. If `Open = 1`, the forecast is unchanged; if `Open = 0`, the forecast becomes zero.

### Prompt 2:

> Now, use `outputs/final_scores.csv` to recompute TimesFM's WAPE as `absolute_error_sum / actual_sum`, showing the values and division.

**Key parts of Codex's reply:**

Codex reported:

```text
absolute_error_sum = 975,525.746459961
actual_sum         = 5,824,198

WAPE = 975,525.746459961 / 5,824,198
     = 0.1674952923
```

Therefore, TimesFM's WAPE is approximately **0.1675**, or **16.75%**.

### Prompt 3:

> Help me gather and verify the numerical and technical evidence needed for Q3 of the assignment. My selected method is TimesFM. Do not write my assignment responses, make conclusions for me, or modify any files. For Q3a, use `outputs/paired_mae.csv` to report the TimesFM minus weekday mean MAE difference and 95% interval and the TimesFM minus seasonal naive MAE difference and 95% interval, and state whether zero falls within each interval. Inspect `VD2_analysis.py` and explain technically how these intervals are calculated and how stores are resampled.

**Key parts of Codex's reply:**

| Comparison | TimesFM minus baseline MAE | 95% interval | Zero in interval? |
|---|---:|---:|---|
| TimesFM − weekday mean | -2.0622 | [-59.2552, 77.6414] | Yes |
| TimesFM − seasonal naive | -46.6622 | [-157.2009, 79.5812] | Yes |

Codex explained that the script:

- Aggregates absolute errors by `(Store, method)`.
- Uses the 20 stores as the resampling units.
- Generates 1,000 bootstrap samples with replacement using a fixed random seed.
- Uses the same sampled stores for each method, preserving the paired comparison.
- Calculates TimesFM minus baseline MAE for each bootstrap sample.
- Uses the 2.5th and 97.5th percentiles of the bootstrap differences as the 95% interval.

### Prompt 4:

> Why does `VD2_analysis.py` resample stores rather than individual store-days when constructing the bootstrap intervals? Base your answer on the structure of the forecasting data and the analysis. Also explain what kind of uncertainty this store bootstrap captures and what kind of uncertainty that it does not capture. Do not write my assignment response for me.

**Key parts of Codex's reply:**

- Each store contributes 42 forecast days, and errors within a store form a time series and may be dependent.
- Resampling entire stores keeps each store's 42-day error pattern together instead of treating the daily errors as independent observations.
- The same resampled stores are used for all methods, preserving the paired comparison.
- The store bootstrap captures variation associated with which stores are included and differences in relative forecasting performance across stores.
- It does not capture uncertainty from different future dates, forecast origins, unobserved future demand shocks, or model-generation uncertainty.

### Prompt 5:

> For Q3b, use `outputs/validation_by_origin.csv` to report all three methods' MAEs for Validation A and Validation B and identify the lowest in each; use `outputs/final_scores.csv` to do the same for the final window; and use `outputs/final_groups.csv` to report all three methods' MAEs and the lowest method for the five Sunday-trading stores and the other fifteen stores. Organize the values so I can compare the rankings and sizes of the gaps myself.

**Key parts of Codex's reply:**

| Window/group | Seasonal naive | Weekday mean | TimesFM | Lowest MAE |
|---|---:|---:|---:|---|
| Validation A | 1763.56 | 1368.75 | 1369.06 | Weekday mean |
| Validation B | 1095.47 | 1117.76 | 1027.02 | TimesFM |
| Final window | 1208.00 | 1163.40 | 1161.34 | TimesFM |
| Sunday-trading stores | 1324.15 | 1500.38 | 1582.48 | Seasonal naive |
| Other 15 stores | 1169.29 | 1051.08 | 1020.96 | TimesFM |

### Prompt 6:

> For Q3c, use `outputs/calendar_check.csv` to report the raw and known-schedule MAE for all three methods, including the change for each method, and inspect the code to explain mechanically why the adjustment changes some methods but not others.

**Key parts of Codex's reply:**

| Method | Raw MAE | Known-schedule MAE | Change |
|---|---:|---:|---:|
| Seasonal naive | 1208.00 | 1208.00 | 0.00 |
| Weekday mean | 1163.40 | 1163.40 | 0.00 |
| TimesFM | 1198.02 | 1161.34 | -36.68 |

Codex found 90 closed store-days. Seasonal naive and weekday mean already had zero raw forecasts on all closed days, so the adjustment did not change their MAEs. TimesFM had nonzero raw forecasts on 45 closed days. Multiplying those forecasts by `Open = 0` changed them to zero, eliminating the associated closed-day error and reducing its MAE.

### Prompt 7:

> For Q3d, use `outputs/interval_coverage.csv` to report TimesFM's interval coverage and row count for all days and open days only, the average interval width for each, and what happens to q10, q90, and actual sales on closed days. Also confirm from the supplied analysis that q10 is checked to be less than or equal to q90 on every row. Give me the factual results and mechanics needed to develop my own interpretations.

**Key parts of Codex's reply:**

| Universe | Rows | Covered rows | Coverage | Average interval width |
|---|---:|---:|---:|---:|
| All days | 840 | 765 | 91.07% | 4888.34 |
| Open days only | 750 | 675 | 90.00% | 5474.94 |

- There are 90 closed-day TimesFM rows.
- On all 90 closed days, `q10 = 0`, `q90 = 0`, and actual sales = 0.
- Closed-day coverage is therefore 100%, with interval width equal to zero.
- The script checks the stronger ordering condition `q10 <= q80 <= q90` before using the supplied forecasts.

### Prompt 8:

> For Q3d, help me understand the evidence needed for my interpretation without writing my assignment response. Using `outputs/interval_coverage.csv`, `outputs/final_predictions.csv`, and `VD2_analysis.py`, explain what happens to TimesFM's q10 and q90 intervals on closed days and why this affects all-days versus open-days coverage. Also explain what the reported average interval width represents and why coverage should be considered together with interval width. Finally, explain technically what uncertainty the q10-q90 forecast range represents compared with the bootstrap 95% MAE-difference interval from Q3a.

**Key parts of Codex's reply:**

- On closed days, multiplying `q10` and `q90` by `Open = 0` makes both endpoints zero. Since actual sales are also zero, all 90 closed days are automatically covered by zero-width intervals.
- All-days coverage is `765 / 840 = 91.07%`, while open-day coverage is `675 / 750 = 90.00%`. The deterministic closed days therefore increase the all-days coverage rate.
- Average interval width is the average value of `q90 - q10`. It is smaller for all days because the 90 closed days contribute widths of zero.
- Coverage should be considered with interval width because wider intervals can produce greater coverage while being less precise.
- The TimesFM `q10` to `q90` interval represents uncertainty about the sales outcome for an individual store-day.
- The Q3a bootstrap 95% interval instead represents uncertainty in the estimated difference in MAE between forecasting methods across the evaluation sample.

### Prompt 9:

> Can you save a transcript of this codex session to case2_owensimon.csv under the AI disclosure section 6? Include only my prompts and key parts of each reply

**Confirmation Response:**

Updated the `## AI record` section in /C:/Users/owens/Repositories/TG-MKTG-6620/2 - Foundation Models for Forecasting/case2_owensimon.md with the substantive prompts and key replies.
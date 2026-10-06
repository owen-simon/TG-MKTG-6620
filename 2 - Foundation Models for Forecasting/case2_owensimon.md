# Case 2 — [Your name]

Choice record: On October 5, 2026, after seeing the validation table,
I chose timesfm because it had the lowest validation mae.

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

- **Seasonal naive:** The seasonal naive method uses the last complete week of training data and repeats it to forecast the next 42 days.
- **Weekday mean:** The weekday mean method uses the last 56 days of training data to calculate an average for each day of the week. These weekday averages are then used to forecast the next 42 days.
- **TimesFM:** TimesFM uses the last 84 observed days of training data to forecast the next 42 days. 
    - The TimesFM forecasts were supplied to me rather than generated or fitted by me.

### 1c AI use, commands, and versions

I used AI to help troubleshoot my Python environment and clarify the assignment instructions. I checked and understood that TimesFM had the lowest validation MAE of 1198.04 and that it also had the lowest final MAE of 1161.34. 

I ran the following using Python 3.11.17, pandas 2.0.0, and NumPy 1.24.2.:

```
python VD2_analysis.py compare --csv data/train.csv --out outputs 
python VD2_analysis.py evaluate --csv data/train.csv --out outputs --choice timesfm 
```

## Q2 — Is the test fair, and how accurate is each method?

### 2a Data

The final window included 20 stores and 840 store-days for each method. The agent confirmed that there were no repeated store-dates or missing forecasts. The `Customers` column was excluded because it represents a contemporaneous count; customer count for a future day would not be known when the forecast is made, so using it would introduce future information.

### 2b Fair test

codex resume 01a10e7e-42f9-7ba3-a13b-6c536a735db5

### 2c Accuracy

## Q3 — How sure are we, and does the result hold up?

### 3a Uncertainty

### 3b Does the ranking hold?

### 3c The closed-day adjustment

### 3d TimesFM's forecast range

## Q4 — Your choice and what would change it

### 4a Choice record

### 4b Comparison table

### 4c What would change my recommendation

## Q5 — Memo to Rina Kapoor
(at most about 400 words)

## AI record
(your prompts and the key parts of the AI's replies,
including anything that didn't work)
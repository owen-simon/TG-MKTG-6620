# Case 1 - Results

## 1. Data Cleaning Decisions

The dataset contained 7,043 observations and 21 variables, with 1,869 customers who churned and 5,174 who did not. All `customerID` values were unique and nonmissing, and all numeric analysis inputs were finite.

Eleven blank `TotalCharges` values occurred for customers with zero `tenure` and were replaced with zero. No other analysis inputs were missing. The presence of outliers was not assessed or treated. Numeric predictors were scaled and categorical predictors were encoded as part of the preprocessing for logistic regression and boosted trees.

## 2. AUC Across All Three Methods

| **Method**          | **Final-test AUC** |
|---------------------|-------------------:|
| Contract rule       |             0.7373 |
| Logistic regression |             0.8471 |
| Boosted trees       |             0.8497 |

Both logistic regression and boosted trees had higher final-test AUCs than the contract rule, indicating better ability to rank customers by churn risk. Boosted trees had the highest AUC at 0.8497, followed closely by logistic regression at 0.8471.

## 3. Uncertainty

| **Method** | **AUC** | **95% AUC Interval** | **ΔAUC vs. Contract Rule** | **95% ΔAUC Interval** | **Crosses Zero?** |
|------------|-----------:|-----------:|-----------:|-----------:|:----------:|
| Contract rule | 0.7373 | 0.7163 to 0.7557 | — | — | — |
| Logistic regression | 0.8471 | 0.8254 to 0.8699 | 0.1099 | 0.0931 to 0.1284 | No |
| Boosted trees | 0.8497 | 0.8283 to 0.8732 | 0.1124 | 0.0959 to 0.1311 | No |

Neither the logistic regression nor the boosted trees ΔAUC intervals crossed zero when compared with the contract rule, indicating that the observed increases in AUC are unlikely to be explained by sampling variability alone.
# V&D Project 1 Analysis

## Q1 - Generate

[COPY AND PASTE PROMPTING]

## Q2 — Validate the analysis

[Data Errors: Missing, Outliers]

[Data Separation]

I used codex and the prompts provided in `VD1_STUDENT_PACK.html` to read the `churn.csv` file and run the `VD1_analysis.py` script.

Codex ran:
```powershell
python VD1_analysis.py compare --csv churn.csv --out outputs
```

This script was used to evaluate three methods:

- **Contract Rule:** The churn rate for customers within each `Contract` category was calculated using the 60% training data and then assigned to customers in the 20% validation set based on their contract category.

- **Logistic Regression:** [Your description here.]

- **Boosted Trees:** [Your description here.]

Both the logistic regression and boosted tree models used the same 7 input variables to predict `Churn`:

- `tenure`

- `MonthlyCharges`

- `TotalCharges`

- `Contract`

- `InternetService`

- `PaperlessBilling`

- `PaymentMethod`

Method comparison results were saved in the `outputs/` folder. A transcript of my codex conversation was saved as `codex_conversation_transcript.md

Before comparing method performance, I used codex to run data checks and cleaning, which identified:

- 7,043 rows and 21 columns
    - 1,869 `Yes` churn outcomes
    - 5,174 `No` churn outcomes

- 11 blank `TotalCharges`, which were replaced with zeros

- No missing analysis inputs

For the model analysis, the data was split into 3 groups:

- 4,225 training rows

- 1,409 validation rows

- 1,409 final-test rows

| Method | Validation AUC | Top-20% contacts | Observed churn in list |
|---|---:|---:|---:|
| Contract rule | 0.742724 | 281 | 41.64% |
| Logistic regression | 0.838402 | 281 | 61.21% |
| Boosted trees | 0.845558 | 281 | 65.12% |

Boosted trees achieved the highest validation AUC of 0.8456. Of the 3 methods, the top-20% contact list generated using the boosted trees model contained the highest proportion of customers who actually churned.

## Q3 — Assess uncertainty and value

[Break Even Rates]

## Q4 — Explain your choice

### Dated validation model choice

**Date recorded:** [2026-09-15]

**Chosen method:** [boosted trees]

I chose boosted trees as the model becuase it achieved the highest validation AUC (0.846). Additionally, the boosted trees model was also able to create a list of 281 contacts with the largest proportion of actual customer-churn (65.12%).

### Comparison Table

| **Method** | **Final-test AUC** | **ΔAUC vs. contract rule** | **95% interval for ΔAUC** | **Carry forward?** | **Reason** |
|---|---:|---:|---|---|---|
| Contract rule | 0.7373 | — | 0.7163 to 0.7557 | No| Your explanation |
| Logistic regression | 0.8471 | 0.1099 | 0.0931 to 0.1284 | Yes | Your explanation |
| Boosted trees | 0.8497 | 0.1124 | 0.0959 to 0.1311 | Yes | Your explanation |

## Q5 — Decide

<!-- Your notes go here. -->

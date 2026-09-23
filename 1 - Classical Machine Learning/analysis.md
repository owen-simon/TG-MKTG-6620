# V&D Project 1 Analysis

## Q1 - Generate

### Transcript File Locations
- `1 - Classical Machine Learning/`
    - `Codex_Transcript.md`: Transcript of user prompts and AI responses.
    - `PowerShell_Transcript.txt`: Time-stamped transcript of the Codex session in PowerShell.

## Q2 — Validate the analysis

### Data Checks

- 7,043 rows and 21 columns

- 1,869 Yes and 5,174 No

- Unique, nonmissing customer IDs

- Imputed zeros for 11 blank `TotalCharges` values at zero `tenure`

- No missing analysis inputs

- Finite numeric values

### Data Separation

- 4,225 training rows

- 1,409 validation rows

- 1,409 final-test rows

## Q3 — Assess uncertainty and value

[Break Even Rates]

## Q4 — Explain your choice

### Comparison Table

| **Method** | **Final-test AUC** | **ΔAUC vs. contract rule** | **95% interval for ΔAUC** | **Carry forward?** | **Reason** |
|---|---:|---:|---|---|---|
| Contract rule | 0.7373 | — | 0.7163 to 0.7557 | No| Your explanation |
| Logistic regression | 0.8471 | 0.1099 | 0.0931 to 0.1284 | Yes | Your explanation |
| Boosted trees | 0.8497 | 0.1124 | 0.0959 to 0.1311 | Yes | Your explanation |

## Q5 — Decide

<!-- Your notes go here. -->

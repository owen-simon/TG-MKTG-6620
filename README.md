# MKTG 6620 — AI Business Decisions

## Case 1 — Which Customers Should the Retention Team Contact?

### Two Commands

```{powershell}
python VD1_analysis.py compare --csv churn.csv --out outputs
```

```{powershell}
python VD1_analysis.py evaluate --csv churn.csv --out outputs --choice trees
```

### Model Choice
Boosted Trees

### File Locations
- `1 - Classical Machine Learning`
  - `outputs/`
  - `churn.csv`
  - `Codex_Transcript.md`
  - `PowerShell_Transcript.md`

---
name: tree-classification
description: Fit or compare decision trees and tree ensembles for classification, checking input timing, held-out ranking, contact capacity, and probability accuracy.
---

Read the task's outcome, positive class, decision time, capacity, baseline, and
allowed methods. Check whether every input exists when the decision is made.
Exclude identifiers and information learned afterward unless the task gives a
valid reason to use them. Completed-call duration cannot guide a pre-call list.

Use the task's split and settings. Fit encoding, scaling where needed, and models
on training rows only. Compare candidates on validation rows, record selection,
and evaluate afterward. Keep final-test data out of tuning. If time or repeated
customers make a random row split unsuitable, surface that before fitting.

Return AUC alongside the observed positive rate at the stated contact capacity.
Keep the contact count within capacity and break score ties without outcomes.
Check predicted against observed rates overall, in the selected list, and across
probability groups; include group counts. AUC assesses ranking, not calibration.

For model differences, use the same resampled evaluation units for both models
and state the uncertainty covered. Keep feature importance separate from causal
effects. Churn risk is not the effect of a retention offer. Report business value
only under explicit cost and intervention assumptions. Preserve all results and
the assignment's boundary around student-written interpretations and memos.

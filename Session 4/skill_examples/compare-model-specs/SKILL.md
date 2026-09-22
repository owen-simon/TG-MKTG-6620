---
name: compare-model-specs
description: Compare a bounded set of model specifications for a stated business prediction task, using a baseline and separate selection and evaluation evidence.
---

Read the assignment or task contract first. Identify the decision, row unit,
outcome, usable inputs, baseline, candidates, primary metric, and compute budget.
Ask only for missing choices that would change the comparison. Use supplied
methods when the task supplies them; do not expand the search automatically.

Keep candidate methods on the same evaluation rows. Use time-ordered evaluation
for future prediction and keep repeated entities together when needed. Learn
preprocessing from training data. Select using validation evidence, record the
choice, then evaluate it on the reserved test data. Do not use test results to
retune and still call that sample untouched.

Return a table of every attempted specification, its choices, validation result,
and status. Add final-test results only after selection. Compare differences on
the same resamples, at a unit appropriate to the data's dependence. State what
the interval includes and omits. An interval containing zero does not establish
equivalence; a small observed win does not establish business value.

Save code, versions, data identifiers, splits, and outputs. Surface tradeoffs
for the user to decide. For assessed coursework, generate calculations and
explanations for learning, but leave assessed interpretations and memos to the
student under the assignment's AI-use policy.

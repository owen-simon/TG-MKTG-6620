# The One-Page Decision Memo
## MKTG 6620 — template, rules, and a worked example

---

## Overview

Every V&D project and the final exam end the same way: a **one-page memo to a named executive**. It is worth 10 of 100 points on each project — small enough that people under-invest, and the single most transferable thing the course produces. Nobody outside this room will ever ask you for your held-out AUC. They will ask you what to do.

A memo that earns full credit does three things and stops:

| Element | The question it answers | Failure mode it prevents |
|---|---|---|
| **Recommendation** | What should we do, specifically, by when? | A summary of the analysis with no action in it |
| **Evidence** | Why should we believe it, in numbers the reader can check? | Confidence with nothing under it |
| **Falsifier** | What single finding would reverse this recommendation? | A recommendation that no evidence could ever overturn |

The falsifier is what separates this from a book report. If you cannot name something that would change your mind, you have not made a decision — you have made an assertion.

---

## Hard rules

| Rule | Detail |
|---|---|
| **One page** | Letter, 11 pt, 1-inch margins. A second page is not read and is not graded |
| **Named recipient** | Address the executive named in the assignment, by name and title |
| **Your own writing** | ⛔ Not allowed — AI drafting, rewriting, or "polishing" of the memo. This is where we evaluate whether *you* understood what the AI did |
| **No code, no model names in the body** | "The model" is fine. `RandomForestClassifier(n_estimators=500)` is not. Put it in an appendix line if it matters |
| **Numbers carry units and comparisons** | "AUC 0.81" means nothing alone. "AUC 0.81 against a 0.50 coin-flip baseline and 0.74 for the current rules engine" means something |
| **Submitted as PDF** | Committed to your project repo |

---

## Structure

Use these five headings. They are not optional; graders look for them by name.

```
TO:      <Executive name>, <Title>, Bonneville Retail Group
FROM:    <Your name>
DATE:    <Date>
RE:      <One line — the decision, not the method>

RECOMMENDATION
  1–2 sentences. An action, an owner, and a timeframe.

WHAT THE ANALYSIS SHOWS
  3–5 sentences or 3–4 bullets. The numbers that support the
  recommendation, each against a baseline or comparison.

WHAT I CHECKED
  2–3 sentences. How you know the result is not an artifact.
  Name the validation, not the vibe.

WHAT WOULD CHANGE MY MIND
  1–3 sentences. The specific finding that would reverse the
  recommendation, and how you would go get it.

WHAT I AM NOT CLAIMING
  1–2 sentences. The limit of the result — scope, population,
  causality, horizon.
```

**On the `RE:` line.** Write the decision, not the method. `RE: Whether to route Tier-1 tickets through automated triage` — not `RE: LLM classification results`.

---

## The five headings, expanded

### RECOMMENDATION

An action, an owner, a timeframe. Executives read this line and stop; everything below exists to survive their follow-up questions.

- **Good:** "Route the 34% of tickets classified as billing-only to automated resolution starting with a two-week pilot in the Canyon & Co. queue, owned by Customer Care operations."
- **Bad:** "The model performs well and could be useful for ticket triage."

The bad version has no action, no owner, no scope, and no date. It cannot be executed, and it cannot be wrong — which is the tell.

### WHAT THE ANALYSIS SHOWS

Three to five sentences, or three to four bullets. Every number needs a comparison point. A metric with nothing beside it is decoration.

| Instead of | Write |
|---|---|
| "Accuracy was 92%." | "Accuracy was 92%, but 89% of cases are the majority class — so accuracy is nearly uninformative here. Recall on the minority class is 41%." |
| "The forecast was accurate." | "Weekly MAPE of 8.4% against 13.1% for the seasonal-naive baseline the planning team uses today." |
| "The segments were clear." | "Four segments, stable across 50 random restarts (mean adjusted Rand index 0.87), differing most on purchase frequency and banner mix." |

### WHAT I CHECKED

This is where the Validate half of the course pays off. Name the specific check and its result — not that you "validated the model."

- **Good:** "Evaluated on a time-ordered holdout of the final 13 weeks, never used in fitting. Coefficient signs match the direction the CRM team expects on all four spend variables."
- **Bad:** "I validated the model and checked the results carefully."

### WHAT WOULD CHANGE MY MIND

The heart of the memo. A good falsifier is **specific, observable, and would actually stop the action**.

| Weak falsifier | Why it fails | Strong falsifier |
|---|---|---|
| "More data would help." | Always true; changes nothing | "If segment membership cannot be predicted from CRM-available fields, this segmentation cannot be targeted and the recommendation is void." |
| "The model could be wrong." | Not a finding | "If the 13-week holdout period turns out to contain the promotional calendar shift, the MAPE gain is an artifact and the baseline stands." |
| "Results might not generalize." | Vague | "If the lift disappears once we condition on tenure, the effect is a tenure story, not a segment story." |

### WHAT I AM NOT CLAIMING

One or two sentences that fence the result. The most common needed fence in this course is **causal**: nearly every model here is predictive, and a predictive model tells you *whom to act on*, never *what the action will do*.

> "This identifies which members are likely to lapse. It does not establish that the retention offer causes them to stay — that needs an experiment, which Session 8's design would support."

---

## Worked example

Session 3's decision, at full credit. Note that it fits on one page and that every number has something beside it.

```
TO:      Devon Achebe, VP Customer Lifecycle, Bonneville Retail Group
FROM:    A. Student
DATE:    September 14, 2026
RE:      Whether to target Summit Club renewal offers by model score

RECOMMENDATION
Target the top two score deciles with the $15 renewal credit beginning with
the October renewal cohort, and hold the remaining eight deciles at the
current no-offer default. Customer Lifecycle owns the pilot; read results
after two renewal cycles.

WHAT THE ANALYSIS SHOWS
- The model separates lapsers from renewers on a held-out sample: AUC 0.78,
  against 0.50 for chance and 0.63 for the current tenure-band rule.
- Lift is concentrated. The top two deciles contain 44% of all lapses while
  covering 20% of members — that concentration, not the AUC, is what makes
  a targeted offer cheaper than a blanket one.
- Below the fourth decile the model is no better than the tenure rule, which
  is why the recommendation stops at two deciles rather than ranking everyone.

WHAT I CHECKED
Evaluated on a 30% holdout split before any preprocessing, so the scaler and
the feature selection never saw the test rows. Coefficient signs on the
logistic baseline match Customer Lifecycle's stated expectations on tenure,
service-contact count, and banner mix. I also refit on a downsampled
training set and confirmed the ranking held but the predicted probabilities
did not — downsampling inflates them, so the deciles are usable and the raw
probabilities are not.

WHAT WOULD CHANGE MY MIND
If the top-decile members are already renewing at high rates for reasons the
model is picking up as risk — a data-timing artifact where the service
contacts happen *after* the renewal decision — the targeting is backwards.
Pulling the contact timestamps relative to renewal date would settle it in a
day, and I would do that before the pilot scales past one cohort.

WHAT I AM NOT CLAIMING
This ranks members by lapse risk. It does not establish that the $15 credit
causes anyone to renew; the pilot's holdout group is what would establish
that.
```

---

## Common point losses

| What happens | Cost | Fix |
|---|---|---|
| Method narration instead of a decision | Heavy | Delete every sentence describing what you did. If the memo is now empty, you have not made a recommendation |
| Falsifier is "more data" or "the model could be wrong" | Heavy | Name a finding, not a feeling |
| Metrics with no comparison | Moderate | Every number gets a baseline beside it |
| Predictive result described in causal language | Moderate | Search your draft for "causes", "drives", "leads to", "impact of" |
| Runs to two pages | Moderate | Cut WHAT THE ANALYSIS SHOWS to three bullets first — it is always the bloated section |
| Reads like AI wrote it | Fails the integrity rule | It must be your writing. See the syllabus AI-use table |

---

## Self-check before submitting

- [ ] One page
- [ ] Addressed to the executive named in the assignment, by name and title
- [ ] Recommendation contains an action, an owner, and a timeframe
- [ ] Every number has a baseline or comparison beside it
- [ ] The validation named is a specific check with a specific result
- [ ] The falsifier is a finding someone could actually go observe
- [ ] No causal verbs attached to a predictive model
- [ ] Written by you, not drafted or rewritten by an AI tool
- [ ] Exported to PDF and committed to the project repo

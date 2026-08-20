# The Prompt Log
## MKTG 6620 — what it is, why the dead ends are the point, and the format to use

---

## Overview

The prompt log is the record of how you directed the AI. It is worth 5 of the 20 Generate points on every V&D project, and it is the artifact that makes an AI-native course gradeable at all: the code shows *what* was run, the log shows *who decided it*.

**The rule that surprises people: a log containing only the prompts that worked is graded 0.** Not reduced — zero. A clean log is a claim that you specified the analysis correctly on the first attempt, which is either untrue or means you never pushed the model hard enough to learn anything. The iterations are the evidence of judgment. The dead ends are where the course happens.

---

## What goes in

| Include | Exclude |
|---|---|
| Every prompt you sent, in order, verbatim | Retyped or cleaned-up versions of what you "meant" |
| Prompts that produced wrong answers | — |
| Prompts you abandoned mid-thread | — |
| Your one-line note on what the response got wrong | Long transcripts of the model's full output (link to the session instead) |
| The correction prompt and why you wrote it | — |
| Which tool: ChatGPT EDU chat, Codex interactive, or `codex exec` | — |

You do not need to paste the model's full replies — the agent session transcript is committed separately. You need the prompts and your reading of what came back.

---

## Format

Markdown, committed as `prompt_log.md` at the root of your project repo. One entry per prompt.

```markdown
### 7 — Codex interactive — 2026-09-10 19:42

**Prompt**
> Split the data 70/30, scale the numeric columns, and fit a logistic
> regression. Report accuracy.

**What came back**
Accuracy 0.91. It fit the StandardScaler on the full dataframe before
splitting.

**My read**
Two problems. The scaler saw the test rows, so the 0.91 is optimistic.
And accuracy is nearly useless here — the target is 9% positive, so
predicting "no" for everyone scores 0.91 as well. The number that looks
like a good model is exactly the number a useless model produces.

**Next**
Prompt 8 — force the split first, then fit the scaler on train only, and
report AUC and recall on the minority class instead of accuracy.
```

Four fields, every time: **Prompt · What came back · My read · Next.** The *My read* field is the graded one.

---

## Worked fragment — what a real thread looks like

The value is visible in the sequence, not in any single entry.

| # | Prompt (abbreviated) | Outcome | Why it mattered |
|---|---|---|---|
| 1 | "Analyze this dataset and tell me what's interesting." | Six charts, no decision | Learned the model needs a *decision*, not a dataset |
| 2 | "Which members are most likely to lapse?" | Fit a model, reported 91% accuracy | Looked great; was the base rate |
| 3 | "What fraction of the target is positive?" | 8.7% | Confirmed the suspicion in one line |
| 4 | "Redo with a stratified split, fit the scaler on train only, report AUC and recall@top-decile." | AUC 0.78 | The real number |
| 5 | "Downsample the majority class and refit." | AUC held, probabilities shifted up | Found the calibration break — this became the Reconcile entry |
| 6 | "Are the predicted probabilities still calibrated after downsampling?" | Model said yes | **It was wrong.** Checked with a calibration curve; it was not |

Entry 6 is the one that earns the points. The model made a confident, wrong, plausible-sounding claim, and the log shows the student not taking it.

---

## Checklist

- [ ] `prompt_log.md` at repo root
- [ ] Every prompt, in order, verbatim — including the ones that failed
- [ ] Tool named on each entry — whichever you used, and the mode (chat · interactive agent · scripted call)
- [ ] A *My read* line on every entry, in your own words
- [ ] At least one entry where the model was confidently wrong and you caught it
- [ ] the agent session transcript committed alongside

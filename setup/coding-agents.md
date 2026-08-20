# Choosing Your Coding Agent — MKTG 6620
## Any agent, any model, any account. Here is what that means and where the course helps.

**This course does not tell you which AI to use.** Use Codex, Claude Code, Grok, OpenCode, Cursor, or something that did not exist when this was written. Use your University seat or your own personal subscription. Use whichever model is behind it.

What is graded is **Generate → Validate → Decide**: whether you can direct an AI to do an analysis, establish whether its answer holds up, and turn that into a decision someone can act on. That skill does not belong to a vendor, and a course that pinned you to one tool would be teaching you the tool instead of the skill.

> **Why this is stated so plainly.** These tools change monthly. During the build of this course the recommended CLI shipped two versions in twelve days. Anything you learn that is specific to one product has a short shelf life; the habit of checking an AI's work does not.

---

## What this means in practice

| | |
|---|---|
| **Which agent** | Yours. No penalty either way, and no question on any rubric asks which one you used |
| **Which model** | Yours. A stronger model makes the Generate half easier and the Validate half no easier at all |
| **Which account** | University seat or personal subscription, your choice |
| **What you submit** | Code, prompt log, validation artifacts, memo — the same regardless of tool |
| **What we support** | Three agents, in depth. Everything else: worked examples and goodwill |

**Different agents fail differently, and that is a feature.** When the room has used four tools on the same dataset, the reconciliation discussion is far richer than when everyone saw the same mistake. Come prepared to say what yours got wrong.

---

## Cost: nobody is excluded

**This course does not recommend an agent.** It has no opinion about which is best, and it will not develop one — that judgment is yours and it will change during the term anyway.

What the course does guarantee is that **cost is never a barrier**. Your University ChatGPT EDU seat includes Codex at no charge, so if you cannot or would rather not pay for a coding agent, you already have a complete one. That is a floor, not a suggestion. If you already pay for something else, use it and do not give this section another thought.

| Agent | Install | Account |
|---|---|---|
| **Codex** | `brew install --cask codex` or `npm install -g @openai/codex` | Included with ChatGPT EDU — sign in with your uNID |
| **Claude Code** | See Anthropic's install page | Your own Claude subscription |
| **Grok** | See xAI's install page | Your own xAI subscription |

Whichever you pick, sign in and confirm it answers before Session 1. `check_setup.py` accepts any of the three and does not care which you have.

> **Why the course refuses to pick.** Betting the materials on one agent's output would make them wrong the moment that vendor ships a release — and these tools ship constantly. Every number this course grades against comes from the **dataset** or from a **pinned local model**, never from what an agent happened to say. That is why your choice genuinely cannot cost you marks.

---

## Sessions 5, 7 and 8 — when your *program* calls the model

For most of the term you talk to your agent and watch it write Python. From Session 5 you also need the reverse: a model your **script** calls inside a loop, returning structured data the next line of code can use.

This is the one place the tools genuinely diverge, so the course ships **three scripts**, one per supported agent:

| File | Agent | How structured output works |
|---|---|---|
| `templates/agent_call_codex.py` | Codex | Native — schema passed as a **file**, `--output-schema` |
| `templates/agent_call_grok.py` | Grok | Native — schema passed as an **inline string**, `--json-schema` |
| `templates/agent_call_claude.py` | Claude Code | **No schema flag** — the script asks, then checks the reply, then re-asks once if it is malformed |

Copy the one for your agent into your project. All three expose the same two lines:

```python
from agent_call_codex import agent_call          # or _claude / _grok

text = agent_call("Summarise this ticket in one sentence: ...")
data = agent_call("Classify this ticket.", schema=TICKET_SCHEMA)   # returns a dict
```

Check your setup without spending anything:

```bash
python agent_call_codex.py --which
```

> **That third row is a lesson, not a gap.** Claude Code has no flag that forces the shape of a reply, so the script asks for JSON, verifies it got JSON, and asks again if it did not. That is exactly the discipline this course teaches, applied to the tool itself. Read that file even if you use a different agent.

---

## Using a fourth agent

Supported, and genuinely fine. The three scripts are **deliberately near-identical and self-contained** rather than sharing a base module, so you can read one end to end and adapt it:

1. Open the script closest to your tool — native schema support (`codex`, `grok`) or none (`claude`).
2. Change `EXE` and the `_build()` function to your agent's command.
3. Change nothing else.

This is a reasonable thing to ask your agent to do for you, and doing it is a fair answer to "do you understand what this tool is actually doing?" If you build one that works, send it to the instructor and it may ship to next year's cohort with your name on it.

---

## Two things every script does for you

**It caches every call to disk.** Re-running a script does not re-spend your credits or your quota. Delete `.agent_cache/` to force fresh calls. Budget note: develop against a handful of rows, not the full dataset, and only widen once the code is right.

**It writes `agent_log.jsonl`.** Every prompt and reply, appended automatically. **That file is the prompt log your project rubric requires** — you do not have to keep one by hand, and it captures the dead ends, which a hand-written log never does.

---

## What is not allowed

Nothing about tool freedom changes the integrity rules. The reconciliation table and the decision memo are **your own writing**, quizzes are closed to AI entirely, and no confidential or employer data goes into any AI tool regardless of which one you chose or who pays for it. See the syllabus.

Questions: **tianyu.gu@eccles.utah.edu**

# Setup Guide — MKTG 6620
## Everything you need installed before Mon Aug 24, and what to do when a step fails

**Budget 30 minutes.** Everything below is free and provided through the University. There is no API key, no billing account, and no credit card at any point in this course.

Work top to bottom. The last step, `check_setup.py`, tests all seven items and tells you exactly which one is broken — so if you are unsure whether something worked, install it and let the checker decide.

> **Version note — read this once.** These tools ship new releases constantly: during the two weeks this guide was written, one of them shipped twice. **Install commands and version numbers below will drift.** If a command here fails outright, do not fight it — go to the vendor's own install page, which is always current, or email me. Losing an evening to a stale command is not what this course is testing. The Codex commands were verified against the live registries on 2026-08-06 (Homebrew cask `codex`, npm `@openai/codex`); 0.147.0 was live on 2026-08-18.

---

## What you are installing, and why

| # | Tool | What it does in this course | Time |
|---|---|---|---|
| 1 | **ChatGPT EDU** | Reasoning, explanation, thinking out loud. Also the credential for Codex, if Codex is the agent you pick | 5 min |
| 2 | **A coding agent** | Writes and runs Python at your direction. **Your choice which one** — Codex is shown below because it is free with your EDU seat. See `coding-agents.md` | 10 min |
| 3 | **Python 3.11+** | The runtime the agent writes code against | 5 min |
| 4 | **git** | Versioning. How you submit every project | 5 min |
| 5 | **VS Code** | Reading files, code, and outputs | 5 min |
| 6 | **HuggingFace account** | Where every dataset and model in the course comes from | 2 min |
| 7 | **GitHub account** | Where your project repositories live | 2 min |

Only items 1–3 and 6 are needed for the Session 1 lab. Items 4, 5, and 7 are needed from Session 2 onward. Install all seven now regardless — the failure you want to discover is the one you find this week, not at 6:05 PM on opening night.

---

## macOS

### Terminal

Open **Terminal** (Applications → Utilities, or `⌘ Space` and type "Terminal"). Every command below is typed there, one line at a time, pressing Return after each.

### 1 · ChatGPT EDU

1. Go to **chatgpt.com**.
2. Choose **Log in**, then the **SSO / Continue with Google** option, and use your **University of Utah account** (your uNID address). Do **not** use a personal Gmail or a personal ChatGPT account.
3. Confirm the workspace switcher at the top of the sidebar shows the **University of Utah** workspace. If it shows "Personal," switch to the University workspace.

**Why this matters twice over:** the University workspace is what carries the data protections referenced in the syllabus, and — **if you use Codex** — it is the account your Codex seat is attached to. Signing Codex in with a personal account instead is the single most common setup failure in this course, and it fails in a way that looks like success. If you use a different agent this trap does not apply to you, but step 1 still does: ChatGPT EDU is used in its own right all term.

### 2 · A coding agent — your choice

**Pick one. Any of them. The course genuinely does not care**, no rubric asks which you used, and nothing you are graded on comes from what an agent says — every number in this course is a property of the dataset or of a pinned local model.

| Agent | Account it needs | Where to install |
|---|---|---|
| **Codex** | **Included with your ChatGPT EDU seat** — no extra cost | Commands below |
| **Claude Code** | Your own Claude subscription | Anthropic's install page |
| **Grok** | Your own xAI subscription | xAI's install page |

**If cost is a factor, take Codex.** It comes with the seat the University already bought you, so nobody is excluded. That is a floor, not a recommendation. If you already pay for one of the others, use it and skip to step 3.

The two non-Codex install pages are deliberately not reproduced here — they change, and the vendor's page is always right. `coding-agents.md` has the fuller picture, including the three scripts Sessions 5–8 need.

**Installing Codex**

Distributed through Homebrew and npm. Either is fine.

```bash
# Option A — Homebrew (install Homebrew first from brew.sh if you do not have it)
brew install --cask codex

# Option B — npm (requires Node.js 20+ from nodejs.org)
npm install -g @openai/codex
```

Codex ships as a Homebrew **cask**, not a formula — `brew install codex` normally resolves to it anyway, but the explicit `--cask` form avoids ambiguity with the unrelated `codex-acp` formula.

Then sign in — **with the same University account as step 1**:

```bash
codex login
```

A browser window opens. Complete the sign-in there, return to the terminal, and confirm:

```bash
codex --version
```

Any version at or above `codex-cli 0.146` is fine; a *higher* number than the one printed here is expected, not a problem. If you want a fuller picture of what Codex thinks of your machine — install method, config, auth state, sandbox — run `codex doctor`.

**Whichever agent you chose**, confirm it actually answers before class: run it once, ask it anything, and see that it replies. `check_setup.py` accepts any of the three.

### 3 · Python 3.11 or newer

macOS ships with a Python, and it is usually too old or too locked down. Install your own.

1. Download the macOS installer from **python.org/downloads** — take the latest 3.12 or 3.13.
2. Run it. Accept the defaults.
3. Confirm in a **new** terminal window:

```bash
python3 --version      # expect 3.11 or higher
python3 -m pip --version
```

On macOS the command is `python3`, not `python`. Use `python3` everywhere in this guide and everywhere in the course.

Install the course packages:

```bash
python3 -m pip install pandas numpy scikit-learn matplotlib datasets
```

### 4 · git

```bash
git --version
```

If macOS offers to install the Command Line Developer Tools, accept — that installs git. Otherwise download from **git-scm.com/downloads**.

Then set your identity, which git needs before it will let you commit:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@utah.edu"
```

### 5 · VS Code

Download from **code.visualstudio.com**, drag to Applications, open it once. When it offers to install the Python extension, accept.

### 6 · HuggingFace account

Sign up at **huggingface.co/join**. Free. No account settings to change; you need it so that dataset downloads are attributed and rate-limited generously.

### 7 · GitHub account

Sign up at **github.com** using your Eccles email. Free.

---

## Windows

### Terminal

Open **Windows Terminal** from the Start menu (or **PowerShell** if Windows Terminal is not installed). Every command below goes there.

### 1 · ChatGPT EDU

Identical to macOS. Go to **chatgpt.com**, log in through **SSO / Continue with Google** with your **uNID University account**, and confirm the workspace switcher shows **University of Utah** and not "Personal."

### 2 · A coding agent — your choice

Same rule as macOS: **any agent, your choice.** Codex is written out because it is free with your EDU seat; Claude Code and Grok are installed from their vendors' own pages, and `coding-agents.md` has the detail.

**Installing Codex**

Install Node.js 20+ from **nodejs.org** (the LTS installer, defaults are fine), then:

```powershell
npm install -g @openai/codex
```

**Close and reopen your terminal.** Windows does not refresh PATH inside an already-open window, and a freshly installed CLI will look missing until you do. This accounts for most "not recognized" reports — and it applies to whichever agent you install, not just Codex.

Then sign in — **with the same University account as step 1**:

```powershell
codex login
codex --version
```

**Whichever agent you chose**, confirm it actually answers before class: run it once, ask it anything, and see that it replies. `check_setup.py` accepts any of the three.

### 3 · Python 3.11 or newer

1. Download from **python.org/downloads** — the latest 3.12 or 3.13, 64-bit.
2. **On the first installer screen, tick "Add python.exe to PATH" before clicking Install.** This checkbox is at the bottom, it is off by default, and forgetting it is the most common Windows failure in this course.
3. Choose **Install Now**.
4. Close and reopen your terminal, then confirm:

```powershell
python --version        # expect 3.11 or higher
python -m pip --version
```

On Windows the command is `python`, not `python3`. If `python` opens the Microsoft Store instead of running Python, see the troubleshooting table below.

Install the course packages:

```powershell
python -m pip install pandas numpy scikit-learn matplotlib datasets
```

### 4 · git

Download **Git for Windows** from **git-scm.com/downloads** and run the installer. Accept every default — there are many screens and none of them need changing.

**Close and reopen your terminal**, then:

```powershell
git --version
git config --global user.name "Your Name"
git config --global user.email "you@utah.edu"
```

### 5 · VS Code

Download from **code.visualstudio.com** and run the installer. On the "Select Additional Tasks" screen, tick **Add to PATH**. Open it once and accept the Python extension when offered.

### 6 · HuggingFace account

Sign up at **huggingface.co/join**. Free.

### 7 · GitHub account

Sign up at **github.com** using your Eccles email. Free.

---

## Run the checker

Download `check_setup.py` from Canvas — or clone the course repository if you already have git working — and run it from the folder that contains it.

```bash
# macOS
python3 check_setup.py
```

```powershell
# Windows
python check_setup.py
```

It changes nothing on your machine except downloading one small public dataset into HuggingFace's normal cache folder. It takes one to four minutes, most of that in the last check.

### What it checks

| # | Check | What "PASS" proves |
|---|---|---|
| 1 | **Python** | Version 3.11+ (3.10 passes with a warning; below 3.10 fails) |
| 2 | **pip** | The package installer works for *this* interpreter |
| 3 | **Course packages** | `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `datasets` all import |
| 4 | **git** | The binary runs, and your commit identity is configured |
| 5 | **Your coding agent** | Any supported agent on PATH, reporting a version, and signed in |
| 6 | **Network to HuggingFace** | Your network can reach `huggingface.co` and read a dataset record |
| 7 | **End-to-end dataset load** | An actual download, opened as a dataframe. This is the check that proves the whole chain works |

Each line is prefixed `PASS`, `WARN`, or `FAIL`, and every failure prints its own fix line underneath, indented with `->`.

### What a clean run ends with

```
====================================================================
ALL CHECKS PASSED — you are ready for Session 1.
====================================================================

Reply to the setup email with the block above. See you Aug 24.
```

You may also see `ALL REQUIRED CHECKS PASSED` followed by a list of non-blocking warnings. That is also a pass.

A failing run ends with `N CHECK(S) FAILED:` and the names of the failed checks.

### What to do with the output

**Copy the final block — pass or fail — and reply to the setup email with it, by Thursday, August 20.**

If it failed, do not spend your evening on it. Send the output. A failure the instructor knows about in advance costs nothing; a failure discovered at 6:05 PM on opening night costs the room forty minutes.

---

## Troubleshooting

These are the failures that actually happen, in rough order of frequency.

| Symptom | Cause | Fix |
|---|---|---|
| **Windows:** `'codex'` (or `claude`, or `grok`) `is not recognized` | PATH was set by the installer but your terminal window predates it | Close **every** terminal window and open a new one. If it still fails, restart Windows. If it still fails, reinstall Node.js, then reinstall codex |
| **Windows:** `'python' is not recognized` | The "Add python.exe to PATH" checkbox was not ticked during install | Re-run the python.org installer, choose **Modify**, and enable the PATH option. Reopening the installer is faster and safer than editing PATH by hand |
| **Windows:** typing `python` opens the Microsoft Store | Windows ships a stub that redirects to the Store when no real Python is on PATH | Install from python.org with the PATH box ticked. Then Settings → Apps → Advanced app settings → **App execution aliases**, and turn **off** the `python.exe` and `python3.exe` aliases |
| **macOS:** `python: command not found`, but `python3 --version` works | macOS provides `python3` only; there is no bare `python` | Use `python3` and `python3 -m pip` everywhere. This is normal and not a problem to fix |
| `pip install` succeeds but `import pandas` still fails | You have more than one Python and installed into the wrong one | Always install with `python3 -m pip install ...` (macOS) or `python -m pip install ...` (Windows). The `python -m pip` form guarantees the package lands in the interpreter you are actually running |
| **Check 5 fails:** `Codex is installed but you are not signed in` | No credentials yet, or the browser sign-in did not complete | Run `codex login` and finish the flow in the browser that opens. Sign in with your **uNID University account** |
| **Check 5 fails after a successful-looking sign-in** | Signed in with a personal ChatGPT account instead of the University one | Run `codex logout` (or `codex login` again), and sign in with the University account. Confirm at chatgpt.com that the workspace switcher shows **University of Utah** |
| **Check 5 warns:** `Could not confirm ... sign-in state` | Only Codex exposes a sign-in status command at all, and even that moves between releases; the checker deliberately warns rather than fails | Not a failure. Type `codex` on its own, ask it anything, and confirm it responds. If it does, you are fine |
| **Check 6 or 7 fails:** cannot reach `huggingface.co` | Corporate proxy, corporate VPN, or a filtered work network. This is the single most common blocker on a work laptop | In order: (1) disconnect from your VPN and retry, (2) retry on your phone's hotspot, (3) retry on home wifi. If it works off the corporate network, it is a proxy block — email the instructor and use the browser fallback below in the meantime |
| **Check 7 fails** with an SSL or certificate error | A corporate network appliance is intercepting HTTPS traffic | This cannot be fixed from your side without your IT department. Use the browser fallback. Do not disable certificate verification — you will need that machine for other things |
| **Check 7 warns:** `Skipped — datasets and/or pandas are not installed yet` | Check 3 failed first | Run the `pip install` line from check 3's fix line, then rerun the checker |
| **Check 1 fails:** `Python 3.9.x is too old` | An old system Python is first on PATH | Install 3.12+ from python.org. On Windows, tick the PATH box. On macOS, use `python3` and confirm `which python3` points at the new install |
| **Check 1 warns:** `Python 3.10 works, but 3.11+ is recommended` | You are on 3.10 | Not a failure. 3.10 will get you through the course. Upgrade when convenient |
| **Check 4 warns:** `git identity is not configured` | You have git but never set your name and email | The two `git config --global` lines above. Thirty seconds |
| The checker itself crashes with a `SyntaxError` | The Python running it is very old — older than the checker's own floor | Install 3.12+ from python.org and rerun. The checker is deliberately written to run on old Pythons so it can tell you this, so a SyntaxError means the interpreter is genuinely ancient |
| Everything installs, nothing works, and you are out of patience | It happens | Stop. Email the instructor with the checker output pasted in. Use the browser fallback for the first session. This is a solvable problem and it is not worth your evening |

---

## If your laptop is locked down by corporate IT

Some employers block software installation outright. You are not stuck, and you are not behind.

| Course tool | Browser substitute |
|---|---|
| Any coding-agent CLI | **ChatGPT EDU in the browser** at chatgpt.com, signed in with your uNID |
| Local Python | **Google Colab** at colab.research.google.com — Python in a browser tab, nothing to install |
| Blocked `huggingface.co` | Colab runs on Google's network, not your employer's, so the block does not apply |
| Local git | GitHub's web interface — create the repository and upload files through the browser |

In Colab, install what you need in the first cell:

```python
!pip install datasets
```

**The browser path can complete every graded artifact in this course.** What it costs is the agentic loop: instead of the agent writing code and running it for you, you copy code out of ChatGPT EDU and paste it into Colab, and copy results back. That is slower, and you will feel it from Session 5 onward when the course starts calling models from inside scripts.

So use it as a bridge, not a destination. **Email the instructor in week one** — a locked-down machine is a fifteen-minute problem in August and a three-week problem in October. Options that have worked for previous cohorts include a personal laptop, a loaner from the Eccles technology desk, or an IT exception request that the instructor can help you word.

---

## Coming in Session 2 — the University's research computers

Everything above is for **Session 1**, and it stays valid all term. From **Session 2 (Mon Aug 31)** the course also runs on **CHPC**, the University's research computing service. You work in a browser: nothing to install, nothing to configure, no cost.

Why it is worth your twenty minutes:

- **One environment instead of forty.** "It works on mine but not on yours" stops being possible.
- **Nothing to install.** If your work laptop is locked down, this is a better answer than the browser fallback below.
- **Datasets and models are already cached**, so they load instantly rather than downloading.

Your laptop remains fully supported and every graded artifact can still be produced on it. CHPC is the recommended path, not a requirement.

**You will receive an invitation code by email before Session 2**, along with full instructions, posted on Canvas. Do not do anything about this yet — finish the list above first.

---

## Before Aug 24 — checklist

- [ ] ChatGPT EDU signed in with the uNID account; workspace switcher shows **University of Utah**
- [ ] Your chosen coding agent is installed and prints a version
- [ ] You signed in to it — for Codex, `codex login` **with the University account**
- [ ] You ran it once by hand and it answered
- [ ] `python3 --version` (macOS) or `python --version` (Windows) prints 3.11 or higher
- [ ] `python -m pip install pandas numpy scikit-learn matplotlib datasets` completed without error
- [ ] `git --version` prints a version, and `git config --global user.name` / `user.email` are set
- [ ] VS Code installed and opened once
- [ ] HuggingFace account created
- [ ] GitHub account created
- [ ] `check_setup.py` run, and its final block replied to the setup email **by Thu Aug 20**
- [ ] Laptop charged, and a charger in the bag — it is a four-hour evening block

Questions before class: **tianyu.gu@eccles.utah.edu**, answered within 24 hours on weekdays.

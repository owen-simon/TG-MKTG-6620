#!/usr/bin/env python3
"""
MKTG 6620 — AI Business Decisions
Setup verification for Session 1.

Run this BEFORE the first class:

    python check_setup.py

It checks the seven things this course depends on and tells you exactly which
one is broken and how to fix it. It changes nothing on your machine except for
downloading one small dataset into HuggingFace's normal cache directory.

STDLIB ONLY, ON PURPOSE. This script has to run on a laptop where nothing is
installed yet, so it must not import pandas, datasets, requests, or anything
else that is part of what it is checking. Do not add third-party imports.

Exit code 0 = all required checks passed.
Exit code 1 = at least one required check failed.
"""

# Deliberately avoids 3.7+ syntax (no `from __future__ import annotations`, no
# PEP 585 generics, no subprocess capture_output=/text=). A student running an
# ancient Python must see "your Python is too old", not a SyntaxError from the
# tool that was supposed to tell them that.

import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

COURSE = "MKTG 6620 — AI Business Decisions"
TERM = "Fall 2026"
INSTRUCTOR_EMAIL = "tianyu.gu@eccles.utah.edu"

# The Session 1 smoke-test dataset. Small, public, ungated. Downloading it end
# to end is what actually proves HuggingFace works from this machine — a
# reachability ping does not.
SMOKE_DATASET = "scikit-learn/iris"
SMOKE_URL = f"https://huggingface.co/api/datasets/{SMOKE_DATASET}"


def _on_chpc():
    """True when this is running on CHPC rather than on a student laptop.

    Checked in order of reliability: the CHPC filesystem root exists on every
    CHPC node and nowhere else; the hostname is the fallback. Deliberately
    cheap and side-effect free -- this runs before anything else is trusted.
    """
    if os.path.isdir("/uufs/chpc.utah.edu"):
        return True
    return "chpc.utah.edu" in platform.node().lower()


ON_CHPC = _on_chpc()

# What to tell a student who is missing a package. On a laptop they fix it
# themselves; on CHPC the environment is managed and shared, so a pip install
# either fails or half-succeeds into their home directory and shadows the
# real package later. That second failure is much worse than the first.
CHPC_PACKAGE_ADVICE = (
    "Do NOT run pip install here -- the CHPC environment is shared and managed."
)

MIN_PY = (3, 10)
REC_PY = (3, 11)

# Packages the course needs. Not required to be present when you run this
# checker — the checker tells you how to install them — but their absence is
# reported so you can fix it before class rather than during it.
COURSE_PACKAGES = [
    "pandas",
    "numpy",
    "scikit-learn",
    "matplotlib",
    "datasets",
]
IMPORT_NAME = {"scikit-learn": "sklearn"}


# --------------------------------------------------------------------------
# output helpers
# --------------------------------------------------------------------------

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return platform.system() != "Windows" or "WT_SESSION" in os.environ


_COLOR = _supports_color()


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def ok(msg: str) -> None:
    print(f"  {_c('PASS', '32')}  {msg}")


def warn(msg: str) -> None:
    print(f"  {_c('WARN', '33')}  {msg}")


def fail(msg: str) -> None:
    print(f"  {_c('FAIL', '31')}  {msg}")


def fixline(msg: str) -> None:
    print(f"        -> {msg}")


def header(n: int, total: int, title: str) -> None:
    print()
    print(f"[{n}/{total}] {title}")


# --------------------------------------------------------------------------
# check plumbing
# --------------------------------------------------------------------------

class Results:
    """Accumulates outcomes so the final block can be copy-pasted to the instructor."""

    def __init__(self):
        self.failures = []
        self.warnings = []

    def failed(self, name):
        self.failures.append(name)

    def warned(self, name):
        self.warnings.append(name)


def run_cmd(args, timeout=25):
    """Run a command, returning (returncode, combined output). Never raises."""
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, (proc.stdout or "").strip()
    except FileNotFoundError:
        return 127, "not found"
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except Exception as exc:  # noqa: BLE001 - a checker must never crash
        return 1, f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------

def check_python(r: Results) -> None:
    header(1, 7, "Python")
    v = sys.version_info
    got = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) < MIN_PY:
        fail(f"Python {got} is too old — this course needs "
             f"{MIN_PY[0]}.{MIN_PY[1]} or newer ({REC_PY[0]}.{REC_PY[1]}+ recommended).")
        if ON_CHPC:
            fixline("On CHPC this almost always means you are NOT in the class environment.")
            fixline("Launch the MKTG 6620 Jupyter app from Interactive Apps, open a terminal")
            fixline("from inside it (File -> New -> Terminal), and rerun this checker there.")
            fixline("Running it from a plain login shell picks up the old system Python.")
        else:
            fixline("Install from https://www.python.org/downloads/")
            fixline("On Windows, tick 'Add Python to PATH' in the installer.")
        r.failed("python")
        return
    if (v.major, v.minor) < REC_PY:
        warn(f"Python {got} works, but 3.11+ is recommended.")
        r.warned("python")
    else:
        ok(f"Python {got}")
    print(f"        interpreter: {sys.executable}")
    print(f"        platform:    {platform.platform()}")


def check_pip(r: Results) -> None:
    header(2, 7, "pip (Python package installer)")
    if ON_CHPC:
        ok("Running on CHPC -- packages are provided by the class environment.")
        fixline(CHPC_PACKAGE_ADVICE)
        return
    code, out = run_cmd([sys.executable, "-m", "pip", "--version"])
    if code != 0:
        fail("pip is not available for this Python interpreter.")
        fixline(f"Try: {sys.executable} -m ensurepip --upgrade")
        r.failed("pip")
        return
    ok(out.splitlines()[0] if out else "pip available")


def check_packages(r: Results) -> None:
    header(3, 7, "Course Python packages")
    missing = []
    for pkg in COURSE_PACKAGES:
        mod = IMPORT_NAME.get(pkg, pkg)
        code, _ = run_cmd([sys.executable, "-c", f"import {mod}"], timeout=60)
        if code == 0:
            ok(pkg)
        else:
            fail(f"{pkg} not installed")
            missing.append(pkg)
    if missing:
        if ON_CHPC:
            fixline(CHPC_PACKAGE_ADVICE)
            fixline("Email %s the exact list above; it gets added for everyone." % INSTRUCTOR_EMAIL)
            fixline("If you are in a Jupyter session, confirm you launched the MKTG 6620 app")
            fixline("rather than a generic Python one -- that is the usual cause.")
        else:
            fixline(f"{sys.executable} -m pip install {' '.join(missing)}")
            fixline("This is expected on a fresh machine. Run the line above, then rerun this checker.")
        r.failed("packages")


def check_git(r: Results) -> None:
    header(4, 7, "Git")
    if shutil.which("git") is None:
        fail("git is not on your PATH.")
        fixline("Install from https://git-scm.com/downloads")
        fixline("Windows: install 'Git for Windows' and reopen your terminal afterwards.")
        r.failed("git")
        return
    code, out = run_cmd(["git", "--version"])
    if code != 0:
        fail(f"git found but would not run: {out}")
        r.failed("git")
        return
    ok(out)

    code, name = run_cmd(["git", "config", "--global", "user.name"])
    code2, email = run_cmd(["git", "config", "--global", "user.email"])
    if code != 0 or code2 != 0 or not name or not email:
        warn("git identity is not configured — your commits will be unattributed.")
        fixline('git config --global user.name "Your Name"')
        fixline('git config --global user.email "you@utah.edu"')
        r.warned("git-identity")
    else:
        ok(f"git identity: {name} <{email}>")


# The agents this course ships a scripted path for. Any agent is allowed --
# these are the three with a supported `agent_call_*.py`. See coding-agents.md.
KNOWN_AGENTS = [
    ("codex",  "Codex",       ["codex", "--version"]),
    ("claude", "Claude Code", ["claude", "--version"]),
    ("grok",   "Grok",        ["grok", "--version"]),
]


def check_codex(r: Results) -> None:
    header(5, 7, "A coding agent (yours -- any of them)")
    found = []
    for exe, label, vcmd in KNOWN_AGENTS:
        if shutil.which(exe) is None:
            continue
        code, out = run_cmd(vcmd, timeout=30)
        # Some agents emit housekeeping warnings on stderr before the version
        # (codex does), so take the first line that is not one of those.
        ver = "version not reported"
        if code == 0 and out:
            for line in out.splitlines():
                line = line.strip()
                if line and not line.upper().startswith(("WARNING", "WARN:", "NOTE:")):
                    ver = line
                    break
        found.append((exe, label, ver))

    if not found:
        fail("No coding agent found on your PATH.")
        fixline("This course does not care which one you use. Install any of:")
        fixline("  Codex        brew install --cask codex   |  npm i -g @openai/codex")
        fixline("  Claude Code  see Anthropic's install page")
        fixline("  Grok         see xAI's install page")
        if ON_CHPC:
            fixline("On CHPC, try:  module load codex")
        fixline("If cost is a problem: Codex comes free with your ChatGPT EDU seat.")
        fixline("Using something else entirely? That is fine. See coding-agents.md.")
        r.failed("agent")
        return

    for exe, label, ver in found:
        ok("%s found -- %s" % (label, ver))
    if len(found) > 1:
        print("        you have %d installed; use whichever you prefer" % len(found))

    # Sign-in state. Only Codex exposes a stable status command, and even that
    # moves between releases, so an unrecognised answer is a WARN and never a
    # FAIL -- a false failure here sends students chasing a problem they do
    # not have. For the other agents we say plainly that we cannot check.
    if any(exe == "codex" for exe, _, _ in found):
        code, out = run_cmd(["codex", "login", "status"], timeout=30)
        blob = out.lower()
        if code == 0 and ("logged in" in blob or "signed in" in blob or "authenticated" in blob):
            ok("Codex is signed in.")
            if "chatgpt" in blob:
                print("        confirm this is your UNIVERSITY account, not a personal one")
        elif "not logged in" in blob or "not signed in" in blob or "no credentials" in blob:
            fail("Codex is installed but you are not signed in.")
            fixline("Run: codex login")
            fixline("Sign in with your University ChatGPT EDU account (your uNID).")
            r.failed("agent-login")
        else:
            warn("Could not confirm Codex sign-in state from this version of the CLI.")
            fixline("Run it once by hand and confirm it answers before class.")
            r.warned("agent-login")
    else:
        warn("Cannot verify sign-in for %s automatically."
             % ", ".join(label for _, label, _ in found))
        fixline("Run your agent once by hand and confirm it answers before class.")
        r.warned("agent-login")


def check_network(r: Results) -> None:
    header(6, 7, "Network access to HuggingFace")
    try:
        req = urllib.request.Request(SMOKE_URL, headers={"User-Agent": "mktg6620-setup-check"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        ok(f"Reached huggingface.co and resolved dataset '{SMOKE_DATASET}'.")
        if isinstance(payload, dict) and payload.get("gated"):
            warn("The smoke-test dataset reports as gated, which is unexpected.")
            r.warned("hf-gated")
    except urllib.error.HTTPError as exc:
        fail(f"HuggingFace returned HTTP {exc.code}.")
        fixline("If you are on a corporate VPN, try again on a home or phone connection.")
        r.failed("network")
    except Exception as exc:  # noqa: BLE001
        fail(f"Could not reach huggingface.co ({type(exc).__name__}).")
        fixline("Check your connection. Corporate networks sometimes block this host —")
        fixline(f"if so, email {INSTRUCTOR_EMAIL} before class and we will sort it out.")
        r.failed("network")


def check_dataset_load(r: Results) -> None:
    header(7, 7, "End-to-end dataset load")
    code, _ = run_cmd([sys.executable, "-c", "import datasets, pandas"], timeout=60)
    if code != 0:
        warn("Skipped — `datasets` and/or `pandas` are not installed yet (see check 3).")
        r.warned("dataset-load")
        return

    script = (
        "import warnings; warnings.filterwarnings('ignore')\n"
        "from datasets import load_dataset\n"
        f"d = load_dataset('{SMOKE_DATASET}', split='train')\n"
        "df = d.to_pandas()\n"
        "print('ROWS', len(df))\n"
        "print('COLS', ','.join(map(str, df.columns))[:200])\n"
    )
    code, out = run_cmd([sys.executable, "-c", script], timeout=240)
    if code != 0:
        fail("Could not download and open the smoke-test dataset.")
        for line in out.splitlines()[-4:]:
            print(f"        {line}")
        fixline("This is usually a network or proxy issue rather than a Python one.")
        r.failed("dataset-load")
        return

    rows = next((l.split(None, 1)[1] for l in out.splitlines() if l.startswith("ROWS")), "?")
    cols = next((l.split(None, 1)[1] for l in out.splitlines() if l.startswith("COLS")), "?")
    ok(f"Downloaded '{SMOKE_DATASET}' and opened it as a dataframe: {rows} rows.")
    print(f"        columns: {cols}")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    print("=" * 68)
    print(f"{COURSE} — {TERM}")
    print("Session 1 setup verification")
    print("environment: %s" % ("CHPC (%s)" % platform.node() if ON_CHPC else "your own machine"))
    print("=" * 68)

    r = Results()
    for check in (
        check_python,
        check_pip,
        check_packages,
        check_git,
        check_codex,
        check_network,
        check_dataset_load,
    ):
        try:
            check(r)
        except Exception as exc:  # noqa: BLE001 - never let one check kill the run
            fail(f"{check.__name__} crashed unexpectedly: {type(exc).__name__}: {exc}")
            r.failed(check.__name__)

    print()
    print("=" * 68)
    if not r.failures:
        if r.warnings:
            print("ALL REQUIRED CHECKS PASSED — you are ready for Session 1.")
            print(f"Non-blocking warnings: {', '.join(r.warnings)}")
        else:
            print("ALL CHECKS PASSED — you are ready for Session 1.")
        print("=" * 68)
        print()
        print("Reply to the setup email with the block above. See you Aug 24.")
        return 0

    print(f"{len(r.failures)} CHECK(S) FAILED: {', '.join(r.failures)}")
    print("=" * 68)
    print()
    print("Copy everything above into a reply to the setup email.")
    print(f"Do not spend your evening on this — send it to {INSTRUCTOR_EMAIL}")
    print("and we will fix it, either by email or in the first minutes of class.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

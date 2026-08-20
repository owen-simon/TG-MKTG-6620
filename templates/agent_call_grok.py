#!/usr/bin/env python3
"""
agent_call — call Grok from inside a Python script.   [MKTG 6620]

Sessions 5, 7 and 8 need a model your *program* calls in a loop, that hands
back structured data your next line of code can use. This is that.

    from agent_call_grok import agent_call

    text = agent_call("Summarise this ticket in one sentence: ...")
    data = agent_call("Classify this ticket.", schema=TICKET_SCHEMA)   # dict

WHICH FILE DO I USE? The course ships three, one per supported agent:

    agent_call_codex.py     codex exec --output-schema FILE   schema is a FILE
    agent_call_grok.py      grok -p --json-schema '{...}'      schema is a STRING
    agent_call_claude.py    claude -p --output-format text    no schema flag

Copy the one for your agent into your project. They are deliberately
self-contained and near-identical rather than sharing a base module, so the
file you copy is the whole story and you can read it in one sitting.

USING SOMETHING ELSE? Good — the course does not care which agent you use.
These three are worked examples: read the one closest to your tool, change
the command in `_build()`, keep everything else. That is the supported path
for a fourth agent, and it is a reasonable thing to have your agent do for you.

WHAT YOU GET FOR FREE
  1. Structured output is forced natively by grok via --json-schema.
  2. Every call is cached to disk, so re-running a script does NOT re-spend
     your credits. This is the most important line in the file for your bill.
  3. Every call is appended to agent_log.jsonl, which IS the prompt log your
     project rubric asks for. You do not have to keep one by hand.

Verified against grok CLI on 2026-08-18. STDLIB ONLY, on purpose.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

EXE = "grok"
CACHE_DIR = Path(os.environ.get("MKTG6620_CACHE", ".agent_cache"))
LOG_PATH = Path(os.environ.get("MKTG6620_LOG", "agent_log.jsonl"))
TIMEOUT = int(os.environ.get("MKTG6620_TIMEOUT", "180"))


class AgentError(RuntimeError):
    pass


NATIVE_SCHEMA = True


def _build(prompt, schema, key):
    """grok takes the schema as an INLINE JSON STRING, and it implies
    --output-format json, so there is nothing else to set."""
    cmd = [EXE, "-p", prompt]
    if schema is not None:
        cmd += ["--json-schema", json.dumps(schema)]
    return cmd


def _extract_json(text):
    """Pull a JSON object out of a reply that may be wrapped in prose or fences.

    Models are chatty. Asking for "only JSON" is not the same as getting it.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    raise AgentError("Reply contained no parseable JSON object:\n" + text[:600])


def _check_schema(obj, schema):
    """Top-level type and required keys. Deliberately not a full validator --
    the failures that actually bite are a missing key or a wrong type."""
    problems = []
    if schema.get("type") == "object" and not isinstance(obj, dict):
        return ["expected a JSON object, got %s" % type(obj).__name__]
    for k in schema.get("required", []):
        if k not in obj:
            problems.append("missing required key %r" % k)
    tm = {"string": str, "number": (int, float), "integer": int,
          "boolean": bool, "array": list, "object": dict}
    for k, spec in schema.get("properties", {}).items():
        if k in obj and spec.get("type") in tm and not isinstance(obj[k], tm[spec["type"]]):
            problems.append("key %r should be %s, got %s"
                            % (k, spec["type"], type(obj[k]).__name__))
    return problems


def _run(cmd):
    if shutil.which(EXE) is None:
        raise AgentError(
            "%r is not on your PATH. Install it, or copy the script for the "
            "agent you actually use -- see coding-agents.md." % EXE)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise AgentError("Call exceeded %ss. Raise MKTG6620_TIMEOUT if the "
                         "prompt is genuinely long-running." % TIMEOUT)
    if p.returncode != 0:
        raise AgentError("%s exited %d.\nstderr:\n%s"
                         % (EXE, p.returncode, p.stderr[:800]))
    return p.stdout.strip()


def _log(rec):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass                      # never let logging break an analysis


def agent_call(prompt, schema=None, use_cache=True, retries=1):
    """One prompt in, str out -- or dict out when you pass a schema."""
    key = hashlib.sha256(
        json.dumps([EXE, prompt, schema], sort_keys=True).encode()
    ).hexdigest()[:32]
    cache_file = CACHE_DIR / (key + ".json")
    if use_cache and cache_file.exists():
        resp = json.loads(cache_file.read_text(encoding="utf-8"))["response"]
        _log({"ts": time.time(), "agent": EXE, "cached": True,
              "prompt": prompt, "response": resp})
        return resp

    ask = prompt
    if schema is not None and not NATIVE_SCHEMA:
        ask = (prompt + "\n\nRespond with ONLY a JSON object matching this "
               "schema. No prose, no code fences.\n" + json.dumps(schema, indent=2))

    last = None
    for attempt in range(retries + 1):
        raw = _run(_build(ask, schema, key))
        if schema is None:
            out = raw
        else:
            try:
                out = _extract_json(raw)
                bad = _check_schema(out, schema)
                if bad:
                    raise AgentError("Reply did not match the schema: "
                                     + "; ".join(bad))
            except AgentError as exc:
                last = exc
                ask = (prompt + "\n\nYour previous reply was rejected: %s\n"
                       "Respond with ONLY a JSON object matching this schema.\n%s"
                       % (exc, json.dumps(schema, indent=2)))
                continue
        _log({"ts": time.time(), "agent": EXE, "cached": False,
              "attempt": attempt, "prompt": prompt, "response": out})
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps({"response": out}), encoding="utf-8")
        return out
    raise AgentError("Gave up after %d attempts. Last error: %s"
                     % (retries + 1, last))


def main():
    ap = argparse.ArgumentParser(description="Call %s." % EXE)
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("--which", action="store_true",
                    help="report setup and exit -- makes no model call")
    ap.add_argument("--schema", help="path to a JSON Schema file")
    ap.add_argument("--no-cache", action="store_true")
    a = ap.parse_args()
    if a.which:
        where = shutil.which(EXE)
        print("agent      : %s" % EXE)
        print("on PATH    : %s" % (where or "NO -- not installed"))
        print("schema     : %s" % ("native" if NATIVE_SCHEMA
                                   else "prompt-injected, then verified"))
        print("cache dir  : %s" % CACHE_DIR)
        print("prompt log : %s" % LOG_PATH)
        return 0 if where else 1
    if not a.prompt:
        ap.error("give a prompt, or use --which")
    schema = json.loads(Path(a.schema).read_text()) if a.schema else None
    out = agent_call(a.prompt, schema=schema, use_cache=not a.no_cache)
    print(json.dumps(out, indent=2) if isinstance(out, dict) else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Blind reader test: which version of a document reads better?

A reader sees two versions with no labels and picks one. Each pair is shown
twice, once in each order. If the reader picks a different version when the
order flips, the pair counts as a tie.

  reader_test.py judge [MODEL] [OLLAMA_URL]   a local model is the reader
  reader_test.py sheet                        write a blind sheet for a person
  reader_test.py tally ANSWERS                score a person's answers

The model reader must not be the model that wrote the rewrites, because
models favour their own writing.
"""
from __future__ import annotations

import json
import random
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIAL = ROOT / "evals" / "trial"
RESULTS = ROOT / "evals" / "results"
READER = ROOT / "evals" / "reader"

MATCHES = [("with", "original"), ("with", "without"), ("without", "original"),
           ("quirks", "with"), ("quirks", "original"),
           ("plain", "with"), ("plain", "original")]
LABEL = {"plain": "rewrite with the plain-words step", "quirks": "rewrite with habits and slips", "with": "rewrite with the skill", "without": "rewrite without the skill",
         "original": "machine draft"}

QUESTION = """Below are two versions of the same document, Version A and Version B.

Which version would a careful human reader prefer? Judge only the writing: is it clear, natural, and free of padding and empty phrases? Do not prefer a version for being longer or for having more formatting.

First write one sentence giving your reason. Then, on a new line, write exactly "ANSWER: A" or "ANSWER: B".

=== Version A ===
{a}

=== Version B ===
{b}
"""


def texts(name: str) -> dict:
    out = {"original": (TRIAL / "with" / name.replace(".txt", ".original.txt")).read_text(encoding="utf-8").strip(),
            "with": (TRIAL / "with" / name).read_text(encoding="utf-8").strip(),
           "without": (TRIAL / "without" / name).read_text(encoding="utf-8").strip()}
    for arm in ("quirks", "plain"):
        extra = TRIAL / arm / name
        if extra.exists():
            out[arm] = extra.read_text(encoding="utf-8").strip()
    return out


def names() -> list[str]:
    return sorted(p.name.replace(".original.txt", ".txt") for p in (TRIAL / "with").glob("*.original.txt"))


def ask(model: str, url: str, a: str, b: str) -> str | None:
    body = json.dumps({"model": model, "prompt": QUESTION.format(a=a, b=b), "stream": False,
                       "options": {"temperature": 0, "num_predict": 120}}).encode()
    request = urllib.request.Request(url + "/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=900) as response:
        reply = json.loads(response.read())["response"]
    found = re.findall(r"ANSWER:\s*\**\s*([AB])\b", reply)
    return found[-1] if found else None


def summarise(rows: list[dict]) -> dict:
    out = {}
    for first, second in MATCHES:
        mine = [r for r in rows if r["first"] == first and r["second"] == second]
        if not mine:
            continue
        out[f"{first} vs {second}"] = {
            "pairs": len(mine),
            first: sum(1 for r in mine if r["winner"] == first),
            second: sum(1 for r in mine if r["winner"] == second),
            "tie": sum(1 for r in mine if r["winner"] == "tie"),
            "picked_whichever_came_first": sum(1 for r in mine if r.get("position_bias")),
        }
    return out


def show(summary: dict) -> None:
    for match, s in summary.items():
        first, second = match.split(" vs ")
        print(f"{LABEL[first]} against {LABEL[second]}: {s['pairs']} pairs")
        print(f"    preferred the {LABEL[first]}: {s[first]}")
        print(f"    preferred the {LABEL[second]}: {s[second]}")
        print(f"    tie (answer changed with the order): {s['tie']}")


def judge(model: str, url: str) -> int:
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"reader-{re.sub(r'[^a-z0-9]+', '-', model.lower())}.json"
    rows = json.loads(out.read_text())["rows"] if out.exists() else []
    done = {(r["file"], r["first"], r["second"]) for r in rows}
    for name in names():
        t = texts(name)
        for first, second in MATCHES:
            if (name, first, second) in done or first not in t or second not in t:
                continue
            one = ask(model, url, t[first], t[second])       # first shown as A
            two = ask(model, url, t[second], t[first])       # first shown as B
            pick_one = {"A": first, "B": second}.get(one)
            pick_two = {"A": second, "B": first}.get(two)
            winner = pick_one if pick_one and pick_one == pick_two else "tie"
            rows.append({"file": name, "first": first, "second": second,
                         "order_1": pick_one, "order_2": pick_two, "winner": winner,
                         "position_bias": one == "A" and two == "A"})
            out.write_text(json.dumps({"reader": model, "rows": rows, "summary": summarise(rows)}, indent=2) + "\n")
            print(name, first, "vs", second, "->", winner, flush=True)
    show(summarise(rows))
    return 0


def sheet() -> int:
    """Write a sheet a person can judge without knowing which version is which."""
    READER.mkdir(exist_ok=True)
    rng = random.Random(20261126)
    key, lines = {}, ["# Blind reader sheet", "",
                      "For each pair, decide which version you would rather read.",
                      "Write your answers in a text file, one per line, like this:", "",
                      "    1 A", "    2 B", "    3 same", "",
                      "Then run: `python3 scripts/reader_test.py tally your-answers.txt`", ""]
    number = 0
    for name in names():
        t = texts(name)
        for first, second in MATCHES[:2]:
            number += 1
            flip = rng.random() < 0.5
            a, b = (second, first) if flip else (first, second)
            key[str(number)] = {"file": name, "A": a, "B": b}
            lines += [f"## Pair {number}", "", "### Version A", "", t[a], "", "### Version B", "", t[b], "", "---", ""]
    (READER / "sheet.md").write_text("\n".join(lines), encoding="utf-8")
    (READER / "key.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {number} pairs to {READER / 'sheet.md'}. Do not open key.json until you have finished.")
    return 0


def tally(path: str) -> int:
    key = json.loads((READER / "key.json").read_text())
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*(\d+)\W+(A|B|same|tie)\b", line, re.I)
        if not match or match.group(1) not in key:
            continue
        entry, answer = key[match.group(1)], match.group(2).upper()
        sides = {entry["A"], entry["B"]}
        first = "with" if "with" in sides else "without"
        second = (sides - {first}).pop()
        winner = entry[answer] if answer in ("A", "B") else "tie"
        rows.append({"file": entry["file"], "first": first, "second": second, "winner": winner})
    if not rows:
        print("No answers found. Use lines such as '1 A' or '2 same'.")
        return 2
    RESULTS.mkdir(exist_ok=True)
    summary = summarise(rows)
    (RESULTS / "reader-person.json").write_text(json.dumps({"reader": "a person", "rows": rows, "summary": summary}, indent=2) + "\n")
    show(summary)
    return 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "judge":
        sys.exit(judge(sys.argv[2] if len(sys.argv) > 2 else "gemma3:12b",
                       sys.argv[3] if len(sys.argv) > 3 else "http://localhost:11434"))
    if command == "sheet":
        sys.exit(sheet())
    if command == "tally" and len(sys.argv) > 2:
        sys.exit(tally(sys.argv[2]))
    print(__doc__)
    sys.exit(2)

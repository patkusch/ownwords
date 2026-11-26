#!/usr/bin/env python3
"""Measure the checker instead of trusting it.

1. Planted errors: take each sample text, damage it in one known way, and see
   whether `check` notices. A text compared with itself always passes, so any
   finding is caused by the planted damage.
2. Sign counts: score the human samples and the machine drafts, and report how
   often each is flagged.

Usage: bench.py [--write] [--gate]
  --write  save evals/results/bench.json
  --gate   exit 1 if a planted error that must be caught was missed, or if
           more than 2 of the human samples show any sign
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ownwords import claims, facts, tells  # noqa: E402
from ownwords.cli import check  # noqa: E402

MONTH_NAMES = ["January", "February", "March", "April", "June", "July", "August",
               "September", "October", "November", "December"]
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"“])")


def _rng(name: str, kind: str) -> random.Random:
    return random.Random(f"{name}:{kind}")


def _digits(text):
    return [m for m in re.finditer(r"(?<![\w/:.-])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?![\w/:-])", facts.URL_RE.sub(lambda m: " " * len(m.group(0)), text))]


def change_number(text, rng):
    found = _digits(text)
    if not found:
        return None
    m = rng.choice(found)
    old = m.group(0)
    last = int(old[-1])
    new = old[:-1] + str((last + rng.choice([1, 2, 3])) % 10)
    return text[:m.start()] + new + text[m.end():]


def swap_numbers(text, rng):
    found = _digits(text)
    values = sorted({m.group(0) for m in found})
    if len(values) < 2:
        return None
    a, b = rng.sample(values, 2)
    first = next(m for m in found if m.group(0) == a)
    second = next(m for m in found if m.group(0) == b)
    if first.start() > second.start():
        first, second = second, first
    return (text[:first.start()] + second.group(0) + text[first.end():second.start()]
            + first.group(0) + text[second.end():])


def drop_unit(text, rng):
    found = list(re.finditer(r"(\d)\s?(?:%| percent)", text))
    if not found:
        return None
    m = rng.choice(found)
    return text[:m.start()] + m.group(1) + text[m.end():]


def change_month(text, rng):
    found = [m for m in re.finditer(r"\b(" + "|".join(MONTH_NAMES) + r")\b", text)]
    if not found:
        return None
    m = rng.choice(found)
    new = rng.choice([n for n in MONTH_NAMES if n != m.group(0)])
    return text[:m.start()] + new + text[m.end():]


def change_name(text, rng):
    names = sorted(n for n in facts.extract(text)["name"] if len(n) > 3)
    if not names:
        return None
    old = rng.choice(names)
    return re.sub(rf"\b{re.escape(old)}\b", "Kessington", text)


def change_quote(text, rng):
    found = [m for m in facts.QUOTE_RE.finditer(text) if len(m.group(1).split()) >= 3]
    if not found:
        return None
    m = rng.choice(found)
    words = m.group(1).split()
    index = rng.randrange(1, len(words))
    words[index] = "truly"
    return text[:m.start(1)] + " ".join(words) + text[m.end(1):]


def change_link(text, rng):
    m = facts.URL_RE.search(text)
    if not m:
        return None
    return text[:m.start()] + re.sub(r"\.example|\.org|\.com", ".example.net", m.group(0), count=1) + "x" + text[m.end():]


def drop_citation(text, rng):
    m = facts.AUTHOR_CITE_RE.search(text) or facts.BRACKET_CITE_RE.search(text)
    if not m:
        return None
    return text[:m.start()].rstrip() + text[m.end():]


DOUBT_SWAPS = [(r"\bmay\b", "will"), (r"\bmight\b", "will"), (r"\bcould\b", "will"),
               (r"\bsuggests\b", "shows"), (r"\bsuggest\b", "show"),
               (r"\bprobably\s", ""), (r"\bpossibly\s", ""), (r"\bpotentially\s", ""),
               (r"\blikely\b", "certain"), (r"\bappears to\b", "does"), (r"\bseems to\b", "does")]


def drop_doubt(text, rng):
    options = [(p, r) for p, r in DOUBT_SWAPS if re.search(p, text)]
    if not options:
        return None
    pattern, new = rng.choice(options)
    return re.sub(pattern, new, text, count=1)


def drop_roughly(text, rng):
    found = list(re.finditer(r"\b(?:about|approximately|roughly|around|at least|up to|nearly|almost)\s(?=[$€£]?\d)", text, re.I))
    if not found:
        return None
    m = rng.choice(found)
    return text[:m.start()] + text[m.end():]


def flip_negation(text, rng):
    removals = list(re.finditer(r"\b(?:not|never)\s", text))
    inserts = list(re.finditer(r"\b(?:is|was|are|were|will|did|does|has|have)\s", text))
    if removals and rng.random() < 0.5:
        m = rng.choice(removals)
        return text[:m.start()] + text[m.end():]
    if not inserts:
        return None
    m = rng.choice(inserts)
    return text[:m.end()] + "not " + text[m.end():]


def add_certainty(text, rng):
    found = list(re.finditer(r"\b(?:is|was|are|were|will)\s", text))
    if not found:
        return None
    m = rng.choice(found)
    return text[:m.end()] + rng.choice(["definitely ", "certainly ", "always "]) + text[m.end():]


def add_invented_sentence(text, rng):
    return text.rstrip() + " The scheme also won an award from the Halden Trust in 2019.\n"


def add_vague_sentence(text, rng):
    return text.rstrip() + " This matters a great deal to everyone involved.\n"


def _sentences(text):
    return SENT_SPLIT.split(text.strip())


def drop_fact_sentence(text, rng):
    parts = _sentences(text)
    options = [i for i, s in enumerate(parts) if re.search(r"\d", s)]
    if len(parts) < 3 or not options:
        return None
    del parts[rng.choice(options)]
    return " ".join(parts) + "\n"


def drop_plain_sentence(text, rng):
    parts = _sentences(text)
    options = [i for i, s in enumerate(parts)
               if not re.search(r"\d", s) and not facts.extract("x " + s)["name"] and len(s.split()) > 6]
    if len(parts) < 3 or not options:
        return None
    del parts[rng.choice(options)]
    return " ".join(parts) + "\n"


# Planted errors the checker is known not to catch reliably. They are measured
# and published, not gated.
KNOWN_BLIND = {"Two numbers swapped with each other",
               "A sentence with no hard fact removed",
               "A vague sentence with no fact added"}

PLANTS = [
    ("A number changed", change_number),
    ("A percent sign dropped", drop_unit),
    ("A month changed", change_month),
    ("A name changed", change_name),
    ("A word changed inside a quotation", change_quote),
    ("A link changed", change_link),
    ("A citation removed", drop_citation),
    ("A word of doubt removed", drop_doubt),
    ("\"About\" or \"at least\" removed from a figure", drop_roughly),
    ("A \"not\" added or removed", flip_negation),
    ("\"Definitely\" or \"always\" added", add_certainty),
    ("A sentence with an invented fact added", add_invented_sentence),
    ("A sentence holding a number removed", drop_fact_sentence),
    ("Two numbers swapped with each other", swap_numbers),
    ("A sentence with no hard fact removed", drop_plain_sentence),
    ("A vague sentence with no fact added", add_vague_sentence),
]


def samples():
    out = []
    for folder in ("human", "ai"):
        for path in sorted((ROOT / "evals" / folder).glob("*.txt")):
            out.append((folder, path.name, path.read_text(encoding="utf-8")))
    return out


def planted(all_samples):
    rows = []
    for label, plant in PLANTS:
        tried = caught_fail = caught_review = 0
        missed = []
        for folder, name, text in all_samples:
            damaged = plant(text, _rng(name, label))
            if damaged is None or damaged == text:
                continue
            tried += 1
            verdict = check(text, damaged)["verdict"]
            if verdict == "fail":
                caught_fail += 1
            elif verdict == "review":
                caught_review += 1
            else:
                missed.append(name)
        rows.append({"plant": label, "tried": tried, "failed": caught_fail,
                     "flagged_for_review": caught_review, "missed": len(missed),
                     "missed_in": missed[:5]})
    return rows


def sign_counts(all_samples):
    rows = []
    for folder, name, text in all_samples:
        result = tells.score(text)
        rows.append({"set": folder, "file": name, "words": result["words"],
                     "per_1000_words": result["per_1000_words"],
                     "signs": {f["id"]: f["count"] for f in result["found"]}})
    return rows


def main():
    all_samples = samples()
    if not all_samples:
        print("No samples in evals/human or evals/ai.")
        return 2
    plant_rows = planted(all_samples)
    sign_rows = sign_counts(all_samples)
    print(f"Planted errors on {len(all_samples)} texts")
    print(f"{'what was planted':52} tried  fail  review  missed")
    for row in plant_rows:
        print(f"{row['plant']:52} {row['tried']:5} {row['failed']:5} {row['flagged_for_review']:7} {row['missed']:7}")
    print()
    for folder in ("human", "ai"):
        rows = [r for r in sign_rows if r["set"] == folder]
        if not rows:
            continue
        scores = sorted(r["per_1000_words"] for r in rows)
        flagged = sum(1 for s in scores if s > 0)
        print(f"{folder:5}: {len(rows)} texts, {flagged} with any sign, "
              f"middle score {scores[len(scores) // 2]}, highest {scores[-1]}")
    result = {"planted": plant_rows, "signs": sign_rows}
    if "--write" in sys.argv:
        out = ROOT / "evals" / "results"
        out.mkdir(exist_ok=True)
        (out / "bench.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if "--gate" in sys.argv:
        slipped = [r["plant"] for r in plant_rows
                   if r["plant"] not in KNOWN_BLIND and r["missed"]]
        human_flagged = sum(1 for r in sign_rows if r["set"] == "human" and r["signs"])
        if slipped or human_flagged > 2:
            print("\nGATE FAILED:", slipped or f"{human_flagged} human samples flagged")
            return 1
        print("\nGate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

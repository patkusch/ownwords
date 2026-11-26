#!/usr/bin/env python3
"""Compare rewrites made with the skill against rewrites made without it.

Both arms are checked against the same original: the draft with the chatbot's
own remarks left out, as saved by the with-skill arm.

Usage: trial_report.py [--write]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ownwords import plain, tells  # noqa: E402
from ownwords.claims import words  # noqa: E402
from ownwords.cli import check  # noqa: E402

TRIAL = ROOT / "evals" / "trial"
rows = []
for original in sorted((TRIAL / "with").glob("*.original.txt")):
    name = original.name.replace(".original.txt", ".txt")
    before = original.read_text(encoding="utf-8")
    row = {"file": name, "set": "tune" if name[:2] <= "08" else "held",
           "original": {"words": words(before), "signs": tells.score(before)["per_1000_words"], "text": before}}
    for arm in ("with", "without", "quirks", "plain"):
        path = TRIAL / arm / name
        if not path.exists():
            continue
        after = path.read_text(encoding="utf-8")
        result = check(before, after)
        row[arm] = {"verdict": result["verdict"], "words": words(after),
                    "signs": tells.score(after)["per_1000_words"], "text": after,
                    "fail": [f"{f['kind']}: {f['detail']}" for f in result["fail"]],
                    "review": [f"{f['kind']}: {f['detail']}" for f in result["review"]]}
    rows.append(row)

for arm in ("with", "without", "quirks", "plain"):
    done = [r for r in rows if arm in r]
    print(f"\n{arm} the skill: {len(done)} rewrites")
    for verdict in ("pass", "review", "fail"):
        print(f"  {verdict}: {sum(1 for r in done if r[arm]['verdict'] == verdict)}")
    print("  findings at fail level:", sum(len(r[arm]["fail"]) for r in done))
    print("  words kept: %d%%" % round(100 * sum(r[arm]["words"] for r in done)
                                      / max(sum(r["original"]["words"] for r in done), 1)))
    print("  rewrites with any sign left:", sum(1 for r in done if r[arm]["signs"] > 0))
    for r in done:
        if r[arm]["fail"]:
            print(f"    {r['file']}: " + "; ".join(r[arm]["fail"]))
print("\nHow plain each version is, all 16 documents together")
print(f"{'version':22} words  words/sentence  long words %  heavy per 1,000  sentences over 30")
for arm in ("original", "without", "with", "quirks", "plain"):
    joined = "\n\n".join(r[arm]["text"] for r in rows if arm in r)
    if not joined:
        continue
    m = plain.measure(joined)
    print(f"{arm:22} {m['words']:5} {m['words_per_sentence']:15} {m['long_words_percent']:13} "
          f"{m['heavy_per_1000_words']:16} {m['sentences_over_30_words']:18}")
for r in rows:
    for arm in list(r):
        if isinstance(r[arm], dict):
            r[arm].pop("text", None)
if "--write" in sys.argv:
    (ROOT / "evals" / "results").mkdir(exist_ok=True)
    (ROOT / "evals" / "results" / "trial.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")

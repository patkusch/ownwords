"""Command line for ownwords.

  ownwords check BEFORE AFTER   did the rewrite keep every fact and claim?
  ownwords score FILE           which signs of machine drafting are in this text?
  ownwords tells                list the signs, their sources and check dates
  ownwords kept REWRITE FINAL   record what the person changed in a rewrite
  ownwords quirks FILE          add a few small human slips, never to a fact
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import json
import re
import sys
from pathlib import Path

from . import __version__, claims, facts, plain, quirks, tells

EXIT_OK, EXIT_FAIL, EXIT_USAGE, EXIT_REVIEW = 0, 1, 2, 3

PLAIN = {
    "number-lost": "A number is missing", "number-added": "A number appeared",
    "date-lost": "A date is missing", "date-added": "A date appeared",
    "time-lost": "A time is missing", "time-added": "A time appeared",
    "link-lost": "A link is missing", "link-added": "A link appeared",
    "email-lost": "An email address is missing", "email-added": "An email address appeared",
    "citation-lost": "A citation is missing", "citation-added": "A citation appeared",
    "quote-lost": "A quotation was changed or removed", "quote-added": "A quotation appeared",
    "name-lost": "A name is missing", "name-added": "A name appeared",
    "doubt-removed": "A word of doubt was removed, so the claim is now stronger",
    "roughly-removed": "A word such as \"about\" or \"at least\" was removed, so a figure is now exact",
    "how-often-removed": "A word such as \"some\" or \"often\" was removed",
    "certainty-added": "A word of certainty was added",
    "negation-changed": "The number of \"not\" words changed, so a meaning may have flipped",
    "text-grew": "The text got more than a fifth longer",
    "text-halved": "More than half the words are gone",
    "sentences-added": "There are noticeably more sentences than before",
}


def check(before: str, after: str, waive: dict | None = None) -> dict:
    waive = waive or {}
    findings = facts.compare(before, after) + claims.compare(before, after)
    waived = []
    kept = []
    for finding in findings:
        reason = waive.get(finding["kind"])
        if reason:
            waived.append({**finding, "reason": reason})
        else:
            kept.append(finding)
    fails = [f for f in kept if f["level"] == "fail"]
    reviews = [f for f in kept if f["level"] == "review"]
    verdict = "fail" if fails else "review" if reviews else "pass"
    return {"verdict": verdict, "unchanged": before.strip() == after.strip(),
            "fail": fails, "review": reviews, "waived": waived,
            "plain": plain.compare(before, after)}


def _print_check(result: dict) -> None:
    headline = {"pass": "PASS: every fact and claim checked is still there.",
                "review": "REVIEW: no facts changed, but look at the points below.",
                "fail": "FAIL: the rewrite changed something it must not change."}
    print(headline[result["verdict"]])
    for level in ("fail", "review"):
        for finding in result[level]:
            print(f"  [{level}] {PLAIN.get(finding['kind'], finding['kind'])}: {finding['detail']}  ({finding['kind']})")
    for note in result.get("plain", []):
        print(f"  [{note.split(':')[0]}] {note.split(': ', 1)[1]}")
    for finding in result["waived"]:
        print(f"  [waived] {PLAIN.get(finding['kind'], finding['kind'])}: "
              f"{finding['detail']} (reason given: {finding['reason']})")


def _print_score(result: dict, name: str) -> None:
    print(f"{name}: {result['per_1000_words']} points per 1,000 words "
          f"({result['words']} words)")
    if not result["found"]:
        print("  No scored signs found. The scorer only knows a short list, so read the text yourself too.")
    for item in result["found"]:
        print(f"  {item['label']} x{item['count']}: {item['why']}")
        for hit in item["hits"][:5]:
            print(f"      line {hit['line']}: {hit['text']}")
        if len(item["hits"]) > 5:
            print(f"      and {len(item['hits']) - 5} more")
    m = result.get("plain")
    if m:
        print(f"  How plain it is: {m['words_per_sentence']} words per sentence, "
              f"{m['long_words_percent']}% long words, "
              f"{m['sentences_over_30_words']} sentences over 30 words")
        for item in m["heavy_words"][:8]:
            print(f"      line {item['line']}: \"{item['text']}\" could be \"{item['plainer']}\"")
        for item in m["noun_heavy_phrases"][:5]:
            print(f"      line {item['line']}: \"{item['text']}\" hides a verb")
        extra = len(m["heavy_words"]) + len(m["noun_heavy_phrases"]) - min(len(m["heavy_words"]), 8) - min(len(m["noun_heavy_phrases"]), 5)
        if extra > 0:
            print(f"      and {extra} more")
    if result["stale_not_scored"]:
        print("  Not scored because their check date has passed: "
              + ", ".join(result["stale_not_scored"]))


def kept(rewrite: str, final: str) -> dict:
    """List the sentences the person removed from, and added to, a rewrite."""
    split = lambda text: [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    a, b = split(rewrite), split(final)
    removed, added = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            removed += a[i1:i2]
            added += b[j1:j2]
    return {"date": datetime.date.today().isoformat(), "sentences_in_rewrite": len(a),
            "sentences_changed": len(removed), "removed": removed, "added": added}


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ownwords", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="compare a rewrite with the original")
    p_check.add_argument("before")
    p_check.add_argument("after")
    p_check.add_argument("--waive", action="append", default=[], metavar="KIND=REASON",
                         help="accept one kind of finding, with a reason that is shown in the report")
    p_check.add_argument("--strict", action="store_true", help="treat review points as failures")
    p_check.add_argument("--json", action="store_true")

    p_score = sub.add_parser("score", help="count signs of machine drafting")
    p_score.add_argument("files", nargs="+")
    p_score.add_argument("--fail-over", type=float, metavar="POINTS",
                         help="exit 1 if any file scores above this many points per 1,000 words")
    p_score.add_argument("--json", action="store_true")

    p_tells = sub.add_parser("tells", help="list the signs and their check dates")
    p_tells.add_argument("--json", action="store_true")

    p_kept = sub.add_parser("kept", help="record what the person changed in a rewrite")
    p_kept.add_argument("rewrite")
    p_kept.add_argument("final")
    p_kept.add_argument("--log", default=".ownwords/kept.jsonl",
                        help="file to add the record to (default: .ownwords/kept.jsonl)")

    p_quirks = sub.add_parser("quirks", help="add a few small human slips, never to a fact")
    p_quirks.add_argument("file")
    p_quirks.add_argument("-o", "--out", help="where to save the result (default: print it)")
    p_quirks.add_argument("--seed", type=int, default=0, help="change this to get different slips")
    p_quirks.add_argument("--every", type=int, default=90, metavar="WORDS",
                          help="roughly one slip per this many words (default 90)")

    args = parser.parse_args(argv)

    if args.command == "quirks":
        try:
            original = _read(args.file)
        except OSError as error:
            print(error, file=sys.stderr)
            return EXIT_USAGE
        changed, notes = quirks.add(original, seed=args.seed, every=args.every)
        if check(original, changed)["verdict"] != "pass":
            print("A slip would have touched a fact, so nothing was changed.", file=sys.stderr)
            changed, notes = original, []
        if args.out:
            Path(args.out).write_text(changed, encoding="utf-8")
        else:
            print(changed, end="")
        print(f"{len(notes)} slips added on purpose:", file=sys.stderr)
        for note in notes:
            print("  " + note, file=sys.stderr)
        return EXIT_OK

    if args.command == "kept":
        try:
            record = kept(_read(args.rewrite), _read(args.final))
        except OSError as error:
            print(error, file=sys.stderr)
            return EXIT_USAGE
        log = Path(args.log)
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"The person changed {record['sentences_changed']} of "
              f"{record['sentences_in_rewrite']} sentences. Saved to {log}.")
        return EXIT_OK

    if args.command == "check":
        waive = {}
        for item in args.waive:
            kind, _, reason = item.partition("=")
            if not reason.strip():
                print(f"--waive needs a reason: {item}", file=sys.stderr)
                return EXIT_USAGE
            waive[kind.strip()] = reason.strip()
        try:
            result = check(_read(args.before), _read(args.after), waive)
        except OSError as error:
            print(error, file=sys.stderr)
            return EXIT_USAGE
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            _print_check(result)
        if result["verdict"] == "fail" or (args.strict and result["verdict"] == "review"):
            return EXIT_FAIL
        return EXIT_REVIEW if result["verdict"] == "review" else EXIT_OK

    if args.command == "score":
        results, over = {}, False
        for name in args.files:
            try:
                text = _read(name)
                results[name] = tells.score(text)
                results[name]["plain"] = plain.measure(text)
            except OSError as error:
                print(error, file=sys.stderr)
                return EXIT_USAGE
            if args.fail_over is not None and results[name]["per_1000_words"] > args.fail_over:
                over = True
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            for name, result in results.items():
                _print_score(result, name)
        return EXIT_FAIL if over else EXIT_OK

    data = tells.load()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return EXIT_OK
    print("Signs that are scored:")
    for tell in data["tells"]:
        state = "CHECK DATE PASSED, not scored" if tells.is_stale(tell) else f"check again by {tell['review_by']}"
        print(f"  {tell['label']} ({tell['evidence']}; {state})\n      {tell['why']}\n      {tell['source']}")
    print("\nSigns that are deliberately not scored:")
    for item in data["do_not_enforce"]:
        print(f"  {item['sign']}: {item['why']}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

"""Claim lock: notice when a rewrite makes a claim stronger, weaker or opposite.

It counts three kinds of small words before and after: words that soften a
claim, words that harden it, and words that negate it.
"""
from __future__ import annotations

import re

# Words that soften a claim, in three groups.
DOUBT = ["may", "might", "could", "possibly", "perhaps", "potentially", "likely",
         "unlikely", "probably", "appears", "appear", "appeared", "seems", "seem",
         "seemed", "suggests", "suggest", "suggested", "indicates", "indicate",
         "indicated", "preliminary", "arguably", "reportedly", "allegedly"]
ROUGHLY = ["approximately", "roughly", "nearly", "almost", "up to", "at least",
           "at most", "estimated", "an estimated", "more than", "less than",
           "fewer than", "over", "under", "about", "around"]
OFTEN = ["some", "most", "many", "few", "several", "often", "usually",
         "sometimes", "generally", "typically", "tends to", "tend to", "largely",
         "mainly", "mostly", "partly", "in part", "rarely", "occasionally"]
# Words that harden a claim.
CERTAIN = ["proves", "prove", "proved", "proven", "demonstrates", "demonstrate",
           "demonstrated", "confirms", "confirm", "confirmed", "establishes",
           "guarantees", "guarantee", "guaranteed", "always", "all", "every",
           "definitely", "certainly", "clearly", "undoubtedly", "obviously",
           "must", "entirely", "completely", "fully", "the only", "never fails"]
NEGATION_RE = re.compile(
    r"\b(?:not|no|never|none|neither|nor|without|cannot|lacks?|lacked|fails? to|failed to)\b"
    r"|n['’]t\b", re.I)
# "Not just X but Y" is a figure of speech, not a real negation.
RHETORICAL_RE = re.compile(
    r"\b(?:not|n['’]t)\s+(?:just|only|merely|simply|solely)\b|\bno longer just\b", re.I)
SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]+|[^.!?\n]+$", re.M)
NUMBER_NEXT = re.compile(r"\s+(?:[$€£]?\d|a\s|an\s|one\b|two\b|three\b|half\b)", re.I)


def _count(text: str, words: list[str]) -> dict:
    counts = {}
    for word in words:
        if word == "may":
            # Lower case only, so the month of May is not counted.
            hits = len(re.findall(r"\bmay\b", text))
        elif word in ("over", "under", "about", "around"):
            hits = sum(1 for m in re.finditer(rf"\b{word}\b", text, re.I)
                       if NUMBER_NEXT.match(text, m.end()))
        elif word == "all":
            hits = len(re.findall(r"\ball\b(?!\s+(?:right|in all))", text, re.I))
        else:
            hits = len(re.findall(rf"\b{re.escape(word)}\b", text, re.I))
        if hits:
            counts[word] = hits
    # Longer phrases contain shorter ones ("an estimated" holds "estimated").
    if "an estimated" in counts and "estimated" in counts:
        counts["estimated"] -= counts["an estimated"]
        if counts["estimated"] <= 0:
            del counts["estimated"]
    return counts


def _negations(text: str) -> int:
    return len(NEGATION_RE.findall(text)) - len(RHETORICAL_RE.findall(text))


def _lost(before: dict, after: dict) -> list[str]:
    return sorted(w for w, n in before.items() if after.get(w, 0) < n)


def _gained(before: dict, after: dict) -> list[str]:
    return sorted(w for w, n in after.items() if before.get(w, 0) < n)


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][\w'’-]*", text))


def sentences(text: str) -> int:
    return sum(1 for s in SENTENCE_RE.findall(text) if words(s) >= 3)


def compare(before: str, after: str) -> list[dict]:
    findings = []
    doubt_a, doubt_b = _count(before, DOUBT), _count(after, DOUBT)
    rough_a, rough_b = _count(before, ROUGHLY), _count(after, ROUGHLY)
    often_a, often_b = _count(before, OFTEN), _count(after, OFTEN)
    sure_a, sure_b = _count(before, CERTAIN), _count(after, CERTAIN)

    doubt_dropped = sum(doubt_b.values()) < sum(doubt_a.values())
    if doubt_dropped:
        findings.append({"level": "fail", "kind": "doubt-removed",
                         "detail": ", ".join(_lost(doubt_a, doubt_b))})
    if sum(rough_b.values()) < sum(rough_a.values()):
        findings.append({"level": "fail", "kind": "roughly-removed",
                         "detail": ", ".join(_lost(rough_a, rough_b))})
    if sum(often_b.values()) < sum(often_a.values()):
        findings.append({"level": "review", "kind": "how-often-removed",
                         "detail": ", ".join(_lost(often_a, often_b))})
    if sum(sure_b.values()) > sum(sure_a.values()):
        findings.append({"level": "fail" if doubt_dropped else "review",
                         "kind": "certainty-added",
                         "detail": ", ".join(_gained(sure_a, sure_b))})
    neg_a, neg_b = _negations(before), _negations(after)
    if neg_a != neg_b:
        findings.append({"level": "fail", "kind": "negation-changed",
                         "detail": f"{neg_a} before, {neg_b} after"})

    words_a, words_b = words(before), words(after)
    sent_a, sent_b = sentences(before), sentences(after)
    if words_a >= 20:
        if words_b > words_a * 1.2:
            findings.append({"level": "review", "kind": "text-grew",
                             "detail": f"{words_a} words before, {words_b} after"})
        if words_b < words_a * 0.5:
            findings.append({"level": "review", "kind": "text-halved",
                             "detail": f"{words_a} words before, {words_b} after"})
    if sent_b > sent_a * 1.34 + 1:
        findings.append({"level": "review", "kind": "sentences-added",
                         "detail": f"{sent_a} before, {sent_b} after"})
    return findings

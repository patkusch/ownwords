"""Count the dated signs of machine drafting in a text."""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

from .claims import words as count_words

DATA = Path(__file__).with_name("tells.json")


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def is_stale(tell: dict, today: datetime.date | None = None) -> bool:
    today = today or datetime.date.today()
    return datetime.date.fromisoformat(tell["review_by"]) < today


def _line(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _excerpt(text: str, start: int, end: int) -> str:
    left = max(0, start - 25)
    right = min(len(text), end + 25)
    return " ".join(text[left:right].split())


def score(text: str, today: datetime.date | None = None) -> dict:
    """Return every sign found, and a single figure per 1,000 words."""
    data = load()
    total_words = max(count_words(text), 1)
    found, stale, points = [], [], 0.0
    for tell in data["tells"]:
        if is_stale(tell, today):
            stale.append(tell["id"])
            continue
        hits = []
        if "eras" in tell:
            listed = sorted({w for era in tell["eras"].values() for w in era})
            distinct = set()
            for word in listed:
                for match in re.finditer(rf"\b{re.escape(word)}\b", text, re.I):
                    distinct.add(word)
                    hits.append({"line": _line(text, match.start()), "text": match.group(0)})
            if len(distinct) < tell.get("min_distinct", 1):
                hits = []
        else:
            for pattern in tell["patterns"]:
                for match in re.finditer(pattern, text, re.I):
                    hits.append({"line": _line(text, match.start()),
                                 "text": _excerpt(text, match.start(), match.end())})
            if len(hits) < tell.get("min_hits", 1):
                hits = []
        if hits:
            hits.sort(key=lambda h: h["line"])
            points += tell["weight"] * len(hits)
            found.append({"id": tell["id"], "label": tell["label"], "why": tell["why"],
                          "evidence": tell["evidence"], "count": len(hits), "hits": hits})
    return {
        "words": total_words,
        "points": points,
        "per_1000_words": round(points * 1000 / total_words, 1),
        "found": found,
        "stale_not_scored": stale,
    }

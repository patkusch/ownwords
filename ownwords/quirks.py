"""Add a few small, human slips to a text: a misspelling, a dropped comma.

The slips never touch a fact. Numbers, names, quotations, links, citations,
code and headings are left exactly as they are, and so are the small words
that carry how sure a claim is.
"""
from __future__ import annotations

import random
import re

from . import claims, facts

# Misspellings people really make. Lower-case words only.
MISSPELL = {
    "the": "teh", "and": "adn", "because": "becuase", "separate": "seperate",
    "receive": "recieve", "received": "recieved", "until": "untill",
    "tomorrow": "tommorow", "occurred": "occured", "necessary": "neccessary",
    "which": "wich", "their": "thier", "really": "realy", "beginning": "begining",
    "different": "diffrent", "immediately": "immediatly", "happened": "happend",
    "experience": "experiance", "already": "allready", "address": "adress",
    "believe": "beleive", "weird": "wierd", "friend": "freind", "government": "goverment",
    "accommodate": "accomodate", "business": "buisness", "calendar": "calender",
    "finally": "finaly", "interesting": "intresting", "successful": "succesful",
    "with": "wiht", "that": "taht", "from": "form", "just": "jsut", "about": "abuot",
}
APOSTROPHE = {"it's": "its", "that's": "thats", "let's": "lets", "you're": "youre",
              "they're": "theyre", "we've": "weve", "i'm": "im", "there's": "theres",
              "what's": "whats", "i've": "ive"}
OPENERS = ["However", "So", "Also", "Then", "Still", "Now", "Unfortunately",
           "Luckily", "Honestly", "Overall", "Finally", "Meanwhile", "Of course"]

_KEEP_WORDS = {w for group in (claims.DOUBT, claims.ROUGHLY, claims.OFTEN, claims.CERTAIN)
               for phrase in group for w in phrase.split()}
_PROTECT = [facts.URL_RE, facts.EMAIL_RE, facts.QUOTE_RE, facts.BRACKET_CITE_RE,
            facts.AUTHOR_CITE_RE, re.compile(r"`[^`\n]+`"), re.compile(r"```.*?```", re.S),
            re.compile(r"\*\*[^*\n]+\*\*"), re.compile(r"(?m)^\s*#.*$"),
            re.compile(r"\[[^\]\n]*\]\([^)\n]*\)"), re.compile(r"\S*\d\S*")]


def _protected(text: str) -> list[bool]:
    mask = [False] * len(text)
    for pattern in _PROTECT:
        for match in pattern.finditer(text):
            for index in range(match.start(), match.end()):
                mask[index] = True
    return mask


def _candidates(text: str) -> dict[str, list[tuple[int, int, str, str]]]:
    """Every slip that could be made, grouped by kind: (start, end, new, note)."""
    mask = _protected(text)
    free = lambda a, b: not any(mask[a:b])
    out = {"spelling": [], "apostrophe": [], "comma": [], "spacing": [], "small i": [], "full stop": []}
    for match in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)?", text):
        word, a, b = match.group(0), match.start(), match.end()
        if not free(a, b):
            continue
        plain = word.replace("’", "'")
        if plain in MISSPELL and plain not in _KEEP_WORDS:
            out["spelling"].append((a, b, MISSPELL[plain], f"\"{word}\" spelled \"{MISSPELL[plain]}\""))
        if plain.lower() in APOSTROPHE and (plain.islower() or plain in ("I'm", "I've")):
            new = APOSTROPHE[plain.lower()]
            out["apostrophe"].append((a, b, new, f"apostrophe dropped from \"{word}\""))
        if word == "I" and a > 0 and text[a - 1] == " " and text[b:b + 1] == " " and text[a - 2:a - 1] not in ".!?":
            out["small i"].append((a, b, "i", "\"I\" written as a small \"i\""))
    for opener in OPENERS:
        for match in re.finditer(rf"(?:(?<=[.!?]\s)|(?m:^)){opener},(?= )", text):
            comma = match.end() - 1
            if free(match.start(), match.end()):
                out["comma"].append((comma, comma + 1, "", f"comma dropped after \"{opener}\""))
    for match in re.finditer(r"(?<=[a-z]{4})\. (?=[A-Z])", text):
        if free(match.start(), match.end()):
            out["spacing"].append((match.start(), match.end(), ".  ", "two spaces after a full stop"))
    stripped = text.rstrip()
    if stripped.endswith(".") and not stripped.endswith("..") and free(len(stripped) - 1, len(stripped)):
        last_line = stripped.splitlines()[-1]
        if len(last_line.split()) > 4:
            out["full stop"].append((len(stripped) - 1, len(stripped), "", "last full stop left off"))
    return out


def add(text: str, seed: int = 0, every: int = 90, most: int = 8) -> tuple[str, list[str]]:
    """Return the text with a few slips, and a list saying what each one is.

    `every` is roughly how many words there are per slip.
    """
    rng = random.Random(seed)
    pools = {kind: items for kind, items in _candidates(text).items() if items}
    for items in pools.values():
        rng.shuffle(items)
    wanted = max(1, min(most, round(claims.words(text) / max(every, 1))))
    kinds = list(pools)
    rng.shuffle(kinds)
    # Spelling first, then one of each other kind in turn, so the slips vary.
    if "spelling" in kinds:
        kinds.remove("spelling")
        kinds.insert(0, "spelling")
    chosen, used_words = [], set()
    while len(chosen) < wanted and any(pools.values()):
        for kind in kinds:
            if len(chosen) >= wanted:
                break
            while pools[kind]:
                item = pools[kind].pop()
                word = text[item[0]:item[1]].lower()
                overlaps = any(item[0] < c[1] and c[0] < item[1] for c in chosen)
                if overlaps or (kind == "spelling" and word in used_words):
                    continue
                used_words.add(word)
                chosen.append(item)
                break
    chosen.sort()
    out, position, notes = [], 0, []
    for start, end, new, note in chosen:
        out.append(text[position:start])
        out.append(new)
        position = end
        notes.append(f"line {text.count(chr(10), 0, start) + 1}: {note}")
    out.append(text[position:])
    return "".join(out), notes

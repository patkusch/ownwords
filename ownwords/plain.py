"""Measure how plain a text is: sentence length, long words, heavy phrases.

These are not signs of machine drafting. Plenty of people write long
sentences. They are a way to see whether a rewrite made the text easier to
read or harder.
"""
from __future__ import annotations

import re

from . import facts

# Heavy words and phrases with a plainer way to say the same thing.
# This is the project's own list. None of the plain versions changes how sure
# a claim is, so swapping them cannot trip the claim lock.
HEAVY = {
    "utilize": "use", "utilise": "use", "utilizing": "using", "utilising": "using",
    "utilization": "use", "utilisation": "use", "commence": "start", "commenced": "started",
    "facilitate": "help", "facilitates": "helps", "facilitating": "helping",
    "leverage": "use", "leveraging": "using", "subsequently": "later",
    "additionally": "also", "furthermore": "also", "moreover": "also",
    "prior to": "before", "subsequent to": "after", "in order to": "to",
    "for the purpose of": "to", "with regard to": "about", "with respect to": "about",
    "in relation to": "about", "regarding": "about", "in the event that": "if",
    "due to the fact that": "because", "owing to the fact that": "because",
    "at this point in time": "now", "at the present time": "now",
    "in close proximity to": "near", "has the ability to": "can", "is able to": "can",
    "are able to": "can", "a number of": "several", "the majority of": "most",
    "in the near future": "soon", "on a regular basis": "regularly",
    "assist": "help", "assistance": "help", "obtain": "get", "purchase": "buy",
    "sufficient": "enough", "terminate": "end", "endeavour": "try", "endeavor": "try",
    "ascertain": "find out", "methodology": "method", "optimal": "best",
    "individuals": "people", "requirement": "need", "requirements": "needs",
    "numerous": "many", "initiate": "start", "initiated": "started",
    "implement": "carry out", "implemented": "carried out", "implementation": "carrying out",
    "currently": "now", "ensure": "make sure", "ensuring": "making sure",
    "comprehensive": "full", "robust": "strong", "seamless": "smooth",
    "seamlessly": "smoothly", "streamline": "simplify", "optimize": "improve",
    "optimise": "improve", "enhance": "improve", "enhanced": "improved",
    "each and every": "every", "first and foremost": "first", "going forward": "from now on",
    "moving forward": "from now on", "in terms of": "in", "take into consideration": "consider",
    "is indicative of": "shows", "in spite of the fact that": "although",
}
# A verb turned into a noun and propped up by an empty verb.
NOUN_HEAVY = [
    r"\b(?:conduct|conducts|conducted|perform|performs|performed|carry out|carried out|undertake|undertook|undertaken)\s+(?:an?|the)\s+\w+(?:tion|sis|ment|ance|ence|view|sessment)\b",
    r"\b(?:make|makes|made|making|reach|reached|come to|came to)\s+(?:an?|the)\s+(?:decision|determination|recommendation|assessment|improvement|contribution|adjustment)\b",
    r"\b(?:give|gives|gave|provide|provides|provided)\s+(?:an?|the)?\s*(?:consideration|indication|explanation|description|assistance|support) (?:to|of|for)\b",
    r"\b(?:the|an?)\s+\w{4,}(?:tion|sion|ment|ance|ence)\s+of\s+(?:the|an?|our|their|its|this)\b",
    r"\b(?:is|are|was|were)\s+in\s+(?:agreement|compliance|possession|receipt)\b",
]
LONG_WORD = 9
LONG_SENTENCE = 30
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _prose(text: str) -> str:
    """Leave out links, quotations and code, which the rewrite may not change."""
    for pattern in (facts.URL_RE, facts.EMAIL_RE, facts.QUOTE_RE,
                    re.compile(r"```.*?```", re.S), re.compile(r"`[^`\n]+`")):
        text = pattern.sub(" ", text)
    return text


def measure(text: str) -> dict:
    prose = _prose(text)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", prose)
    sentences = [s for s in SENTENCE_RE.split(prose) if len(re.findall(r"[A-Za-z]+", s)) >= 3]
    lengths = [len(re.findall(r"[A-Za-z][A-Za-z'’-]*", s)) for s in sentences]
    heavy = []
    for phrase, simple in HEAVY.items():
        for match in re.finditer(rf"\b{re.escape(phrase)}\b", prose, re.I):
            heavy.append({"line": prose.count("\n", 0, match.start()) + 1,
                          "text": match.group(0), "plainer": simple})
    noun_heavy = []
    for pattern in NOUN_HEAVY:
        for match in re.finditer(pattern, prose, re.I):
            noun_heavy.append({"line": prose.count("\n", 0, match.start()) + 1, "text": match.group(0)})
    heavy.sort(key=lambda h: h["line"])
    noun_heavy.sort(key=lambda h: h["line"])
    total = max(len(words), 1)
    return {
        "words": len(words),
        "words_per_sentence": round(len(words) / max(len(sentences), 1), 1),
        "longest_sentence": max(lengths, default=0),
        "sentences_over_30_words": sum(1 for n in lengths if n > LONG_SENTENCE),
        "long_words_percent": round(100 * sum(1 for w in words if len(w) >= LONG_WORD) / total, 1),
        "heavy_per_1000_words": round(1000 * (len(heavy) + len(noun_heavy)) / total, 1),
        "heavy_words": heavy,
        "noun_heavy_phrases": noun_heavy,
    }


def compare(before: str, after: str) -> list[str]:
    """Say in plain words whether the rewrite got plainer or heavier."""
    a, b = measure(before), measure(after)
    notes = []
    # A change smaller than the step is noise and is not reported.
    for key, label, step in (("words_per_sentence", "words per sentence", 1.0),
                             ("long_words_percent", "long words, percent", 1.0),
                             ("heavy_per_1000_words", "heavy words and phrases per 1,000 words", 2.0),
                             ("sentences_over_30_words", "sentences over 30 words", 1)):
        if b[key] - a[key] >= step:
            notes.append(f"heavier: {label} went from {a[key]} to {b[key]}")
        elif a[key] - b[key] >= step:
            notes.append(f"plainer: {label} went from {a[key]} to {b[key]}")
    return notes

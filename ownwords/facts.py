"""Fact lock: pull the hard facts out of a text and compare two versions.

A "fact" here is anything a rewrite has no business changing: numbers, dates,
times, links, email addresses, quoted words, citations and names.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

MONTHS = {
    "january": "jan", "february": "feb", "march": "mar", "april": "apr",
    "june": "jun", "july": "jul", "august": "aug", "september": "sep",
    "october": "oct", "november": "nov", "december": "dec",
    "jan": "jan", "feb": "feb", "mar": "mar", "apr": "apr", "jun": "jun",
    "jul": "jul", "aug": "aug", "sep": "sep", "sept": "sep", "oct": "oct",
    "nov": "nov", "dec": "dec",
}
DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}

NUMBER_WORDS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}
SCALES = {"hundred": 100, "thousand": 1000, "million": 10**6, "billion": 10**9,
          "trillion": 10**12}

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+|www\.[^\s<>\"')\]]+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
SLASH_DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?", re.I)
BRACKET_CITE_RE = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]")
AUTHOR_CITE_RE = re.compile(
    r"\(([A-Z][A-Za-z'’-]+(?:\s+et al\.?|\s+(?:and|&)\s+[A-Z][A-Za-z'’-]+)?),?\s+(\d{4}[a-z]?)\)"
)
QUOTE_RE = re.compile(r"[\"“]([^\"“”\n]{2,400})[\"”]")
NUMBER_RE = re.compile(
    r"(?P<cur>[$€£])?\s?(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<ord>st|nd|rd|th)?"
    r"(?:\s?(?P<scale>hundred|thousand|million|billion|trillion)\b)?"
    r"(?:\s?(?P<unit>%|percent\b|per cent\b|dollars\b|euros\b|pounds\b))?",
    re.I,
)
WORD_NUMBER_RE = re.compile(
    r"\b(" + "|".join(NUMBER_WORDS) + r")\b"
    r"(?:[\s-](hundred|thousand|million|billion|trillion)\b)?"
    r"(?:\s(percent|per cent)\b)?",
    re.I,
)
MONTH_RE = re.compile(r"\b(" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")\b\.?", re.I)
MAY_RE = re.compile(
    r"(?:\b(?:in|of|on|since|during|until|by|last|next|early|late|mid)\s+May\b)"
    r"|(?:\bMay\s+\d)|(?:\d(?:st|nd|rd|th)?\s+May\b)"
)
DAY_RE = re.compile(r"\b(" + "|".join(DAYS) + r")\b", re.I)
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'’-]*")
SENTENCE_END = set(".!?:")
UNIT_NAMES = {"percent": "%", "per cent": "%", "%": "%", "dollars": "$",
              "euros": "€", "pounds": "£"}

# Capitalised words that are not names when they appear mid-sentence.
NOT_NAMES = {"I", "I'm", "I've", "I'll", "I'd", "OK", "A", "The", "An"}


def _canon(value: Decimal) -> str:
    value = value.normalize()
    text = format(value, "f")
    return text


def _mask(text: str, pattern: re.Pattern, out: set, clean=None) -> str:
    def repl(match: re.Match) -> str:
        found = match.group(0)
        if clean:
            found = clean(found)
        out.add(found)
        return " " * len(match.group(0))
    return pattern.sub(repl, text)


def _clean_url(url: str) -> str:
    return url.rstrip(".,;:!?")


def _clean_quote(quote: str) -> str:
    quote = quote.replace("’", "'").replace("‘", "'")
    return " ".join(quote.split()).strip(" .,;:!?").lower()


def _numbers(text: str) -> tuple[set, bool]:
    found = set()
    for match in NUMBER_RE.finditer(text):
        raw = match.group("num").replace(",", "")
        try:
            value = Decimal(raw)
        except InvalidOperation:
            continue
        scale = (match.group("scale") or "").lower()
        if scale:
            value *= SCALES[scale]
        unit = UNIT_NAMES.get((match.group("unit") or "").lower(), "")
        if match.group("cur"):
            unit = match.group("cur")
        found.add(_canon(value) + unit)
    for match in WORD_NUMBER_RE.finditer(text):
        value = Decimal(NUMBER_WORDS[match.group(1).lower()])
        if match.group(2):
            value *= SCALES[match.group(2).lower()]
        unit = "%" if match.group(3) else ""
        found.add(_canon(value) + unit)
    has_one = bool(re.search(r"\b(one|a single|once)\b", text, re.I))
    return found, has_one


# Common words that open sentences, labels and headings. Never names.
FUNCTION_WORDS = set("""a an the and but or so if as at by for from in into of on to up with
without i we you he she it they my our your his her its their this that these those here
there what when where which who why how while although because since until unless though
after before during over under about against between through all any both each every few
more most many much some such no not only own same other another new please thank thanks
dear hi hello yes ok okay get let see note also however therefore meanwhile then now today
tomorrow yesterday is are was were be been has have had do does did will would can could
should may might must first second third next last finally overall once one two three""".split())

BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
HASHTAG_RE = re.compile(r"#\w+")


def _names(text: str) -> tuple[set, set]:
    """Return (names, every word seen) for one text.

    A name is a capitalised word in running prose that is not simply the first
    word of a sentence. Headings, bold labels, hashtags and short label lines
    are styling, so their capitals do not count.
    """
    names, words, lower_seen = set(), set(), set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for match in TOKEN_RE.finditer(stripped):
            token = match.group(0).strip("'’-")
            if token:
                words.add(token.lower())
                words.add(re.split(r"['’]", token.lower())[0])
                if token[0].islower():
                    lower_seen.add(token.lower())
        if stripped.startswith("#"):
            continue
        body = HASHTAG_RE.sub(" ", BOLD_RE.sub(" . ", stripped))
        body = re.sub(r"^(?:[>*+\-•\d.)\s]|\.)+", "", body)
        plain = body.strip().rstrip("*_ ")
        tokens = list(TOKEN_RE.finditer(body))
        if not tokens:
            continue
        is_sentence = plain.endswith((".", "!", "?", '"', "”", ")")) or len(tokens) > 12
        if not is_sentence:
            # A short line with no full stop: a label, a subject line or a sign-off.
            bare_name = (len(tokens) <= 3 and not plain.endswith(":")
                         and all(t.group(0)[0].isupper() for t in tokens))
            if not bare_name:
                continue
        at_start = True
        position = 0
        for index, match in enumerate(tokens):
            token = match.group(0).strip("'’-")
            if token.endswith(("'s", "’s")):
                token = token[:-2]
            if not token:
                continue
            between = body[position:match.start()]
            if any(ch in SENTENCE_END for ch in between):
                at_start = True
            position = match.end()
            lower = token.lower()
            plain_word = re.split(r"['’]", lower)[0]
            capital = token[0].isupper()
            special = (token.isupper() and len(token) > 1 and not line.isupper()
                       or any(c.isupper() for c in token[1:]) or any(c.isdigit() for c in token))
            if (capital and token not in NOT_NAMES and plain_word not in FUNCTION_WORDS
                    and lower not in MONTHS and lower not in DAYS):
                if not at_start or special:
                    names.add(token)
                else:
                    nxt = tokens[index + 1] if index + 1 < len(tokens) else None
                    if (nxt and nxt.group(0)[0].isupper() and body[match.end():nxt.start()] == " "
                            and nxt.group(0).lower() not in FUNCTION_WORDS):
                        names.add(token)
            at_start = False
    return names, words, lower_seen


def extract(text: str) -> dict:
    """Pull every hard fact out of a text, grouped by kind."""
    facts = {k: set() for k in ("link", "email", "date", "time", "citation",
                                "quote", "number", "name")}
    for match in QUOTE_RE.finditer(text):
        quote = _clean_quote(match.group(1))
        if len(quote.split()) >= 2:
            facts["quote"].add(quote)
    work = _mask(text, URL_RE, facts["link"], clean=_clean_url)
    work = _mask(work, EMAIL_RE, facts["email"], clean=str.lower)
    work = _mask(work, ISO_DATE_RE, facts["date"])
    work = _mask(work, SLASH_DATE_RE, facts["date"])
    work = re.sub(r"\b24/7\b", "    ", work)  # an idiom, not two numbers
    work = _mask(work, TIME_RE, facts["time"], clean=lambda s: re.sub(r"[\s.]", "", s.lower()))
    work = _mask(work, BRACKET_CITE_RE, facts["citation"], clean=lambda s: re.sub(r"\s", "", s))
    for match in AUTHOR_CITE_RE.finditer(work):
        facts["citation"].add(f"({' '.join(match.group(1).split())} {match.group(2)})".replace("et al.", "et al"))
    for match in MONTH_RE.finditer(work):
        word = match.group(1)
        if word[0].isupper():
            facts["date"].add(MONTHS[word.lower()])
    if MAY_RE.search(work):
        facts["date"].add("may")
    for match in DAY_RE.finditer(work):
        if match.group(1)[0].isupper():
            facts["date"].add(match.group(1).lower())
    facts["number"], has_one = _numbers(work)
    names, words, lower_seen = _names(work)
    facts["name"] = names
    facts["_words"] = words
    facts["_lower"] = lower_seen
    facts["_has_one"] = has_one
    return facts


def compare(before: str, after: str) -> list[dict]:
    """List every fact that was lost or added between two versions."""
    a, b = extract(before), extract(after)
    findings = []
    for kind in ("number", "date", "time", "link", "email", "citation", "quote"):
        for item in sorted(a[kind] - b[kind]):
            if kind == "number" and item == "1" and b["_has_one"]:
                continue
            findings.append({"level": "fail", "kind": f"{kind}-lost", "detail": item})
        for item in sorted(b[kind] - a[kind]):
            if kind == "number" and item == "1" and a["_has_one"]:
                continue
            findings.append({"level": "fail", "kind": f"{kind}-added", "detail": item})
    # A capitalised word that either text also writes in lower case is an
    # ordinary word, not a name.
    ordinary = a["_lower"] | b["_lower"]
    for name in sorted(a["name"]):
        if name.lower() in ordinary:
            continue
        if name.lower() not in b["_words"]:
            findings.append({"level": "fail", "kind": "name-lost", "detail": name})
    for name in sorted(b["name"]):
        if name.lower() in ordinary:
            continue
        if name.lower() not in a["_words"]:
            findings.append({"level": "fail", "kind": "name-added", "detail": name})
    return findings

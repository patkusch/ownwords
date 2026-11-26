#!/usr/bin/env python3
"""Fetch human writing from before chat models existed.

Wikipedia articles as they stood on 1 January 2021. Each sample is the first 450 or so words of running prose.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evals" / "human"
AGENT = {"User-Agent": "ownwords-test-data/0.1 (open-source test fixture fetch)"}
WIKI = ["Lighthouse", "Sourdough", "Tram", "Beekeeping", "Canal", "Compost",
        "Bicycle", "Tide", "Bread", "Windmill", "Ada Lovelace", "Great Fire of London",
        "Photosynthesis", "Marie Curie", "Printing press", "Suez Canal"]


def get(url):
    for wait in (5, 20, 60, 120):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503):
                raise
    raise SystemExit("the site kept refusing: " + url)


def strip_wikitext(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    for _ in range(6):
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
        text = re.sub(r"\{\|[^{}]*?\|\}", "", text, flags=re.S)
    text = re.sub(r"\[\[(?:File|Image|Category):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", text)
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "").replace("&nbsp;", " ")
    paras = [p.strip() for p in text.split("\n")
             if len(p.split()) > 40 and not p.lstrip().startswith(("=", "*", "#", "|", "!", ":", "{", "["))]
    return paras


def take(paras, limit=450):
    out, total = [], 0
    for p in paras:
        out.append(p)
        total += len(p.split())
        if total >= limit:
            break
    return "\n\n".join(out) + "\n"


sources = []
for title in WIKI:
    api = ("https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions"
           "&rvlimit=1&rvstart=2021-01-01T00:00:00Z&rvdir=older&rvprop=ids|timestamp|content"
           "&rvslots=main&titles=" + urllib.parse.quote(title))
    page = next(iter(json.loads(get(api))["query"]["pages"].values()))
    rev = page["revisions"][0]
    text = take(strip_wikitext(rev["slots"]["main"]["*"]))
    name = "wiki-" + title.lower().replace(" ", "-") + ".txt"
    (OUT / name).write_text(text, encoding="utf-8")
    sources.append((name, f"Wikipedia, \"{title}\", revision of {rev['timestamp'][:10]}",
                    f"https://en.wikipedia.org/w/index.php?title={urllib.parse.quote(title)}&oldid={rev['revid']}", "CC BY-SA 4.0"))
    print(name, len(text.split()))


lines = ["# Where the human samples come from", "",
         "All of this was written before chat models existed. Each file is an excerpt.", "",
         "| File | Source | Link | Licence |", "|---|---|---|---|"]
lines += [f"| {n} | {s} | {u} | {l} |" for n, s, u, l in sources]
(OUT / "SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

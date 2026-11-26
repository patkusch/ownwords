#!/usr/bin/env python3
"""Ask a local model to draft each brief, so the tests have machine drafts
that nobody on this project wrote or tuned.

Usage: make_ai_samples.py MODEL [OLLAMA_URL]
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
model = sys.argv[1] if len(sys.argv) > 1 else "gemma3:4b"
url = (sys.argv[2] if len(sys.argv) > 2 else "http://localhost:11434") + "/api/generate"

for item in json.loads((ROOT / "evals" / "briefs.json").read_text()):
    out = ROOT / "evals" / "ai" / f"{item['id']}.txt"
    if out.exists():
        continue
    body = json.dumps({"model": model, "prompt": item["brief"], "stream": False,
                       "options": {"temperature": 0.7, "seed": 7}}).encode()
    request = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=600) as response:
        text = json.loads(response.read())["response"].strip()
    out.write_text(text + "\n", encoding="utf-8")
    print(item["id"], len(text.split()), "words", flush=True)

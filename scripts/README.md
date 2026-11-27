# Scripts

| Script | What it is for |
|---|---|
| `ownwords` | Runs the checker. This is the one most people need. |
| `bench.py` | Damages each sample text in a known way and counts how often the checker notices. CI runs it with `--gate`. |
| `trial_report.py` | Compares rewrites made with the skill against rewrites made without it. |
| `reader_test.py` | Runs the blind reader test, with a local model or a person as the reader. |
| `make_ai_samples.py` | Wrote the machine drafts in `evals/ai`. Needs a local model. |
| `fetch_human_samples.py` | Fetched the human samples in `evals/human` from Wikipedia. |

The last two were used once to build the sample sets. You do not need to run them again.

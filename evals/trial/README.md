# The trial: with the skill and without it

Two agents each rewrote the 16 machine drafts in `evals/ai`.

- `without/`: told only to make the text read like a careful person wrote it.
- `with/`: told to follow `SKILL.md`. Each draft has the saved original, the rewrite and the hand-over notes.

`python3 scripts/trial_report.py` checks both sets against the same originals.

To repeat it, give two fresh agents the same two instructions and run the report again. Neither agent may see the other's folder, and the first may not see the skill.

# How ownwords is allowed to change

The skill and the checker will keep changing. This page says which changes are allowed in.

## The three test sets

| Set | Where | Used for |
|---|---|---|
| Tuning drafts | `evals/ai/01` to `08` | Looked at freely when writing rules. |
| Held-out drafts | `evals/ai/09` to `16` | Scored, never read while writing a rule. |
| Past failures | `evals/regressions/cases.json` | Every mistake found so far. Each one must stay fixed. |

The human samples in `evals/human` guard against flagging real people's writing.

## Where ideas for a change come from

1. A planted error the checker missed (`python3 scripts/bench.py`).
2. A check that fired on a faithful rewrite, found in a trial run.
3. A person undoing one of the skill's edits (`ownwords kept`).
4. A sign whose check date has passed (`ownwords tells`).

## The rule

A change ships only if all of these hold.

1. **No planted error slips.** Every planted error that was caught before is still caught. CI runs this on every push.
2. **No past failure returns.** Every case in `cases.json` still gives its expected result. CI runs this too.
3. **Real writing stays unflagged.** No more than 2 of the 16 human samples show any sign.
4. **Held-out results do not get worse.** On drafts 09 to 16, the rewrite arm with the skill has no more real fact changes than before the change.
5. **A new sign needs a source and a check date.** No source, no sign.
6. **Nothing is tuned against an AI detector.** A detector score is never a reason for a change.

Steps 1 to 3 and 5 are automatic. Step 4 needs a trial run with two agents, as described in `evals/trial/README.md`. It is done by hand before a release.

## Rejected changes

A change that fails the rule goes in [REJECTED.md](REJECTED.md) with the numbers, so nobody tries it twice.

## What is not automatic yet

- Turning a person's edits into a proposed rule change. `ownwords kept` only records them.
- A reader test with people. `scripts/reader_test.py` runs one with a local model, which is a weak reader.
- Retiring a stale sign. The scorer stops counting it, but a person must re-check the source and move the date.

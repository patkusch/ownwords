# Contributing

Thanks for looking. This project is small on purpose.

## Run the tests

```bash
python3 -m unittest discover -s tests
```

```bash
python3 scripts/bench.py --gate
```

Both must pass. Nothing needs installing beyond Python 3.10 or newer.

## What gets in

- **A fix for a false alarm or a missed change.** Add the case to `evals/regressions/cases.json` first, so it stays fixed.
- **A new sign of machine drafting.** It needs a public source, the date it was added, and a date to check it again. See `ownwords/tells.json`.
- **A change to the skill.** It has to pass the ship rule in [docs/SHIP-RULE.md](docs/SHIP-RULE.md).

## What does not get in

- Anything meant to get text past an AI detector.
- A sign with no source. "It feels like AI" is not a source.
- A dependency. The checker runs on plain Python.

Changes that were tried and turned down are listed in [docs/REJECTED.md](docs/REJECTED.md). Please read it before proposing one of them again.

## Security

See [SECURITY.md](SECURITY.md).

# Examples

Three short texts to try the checker on.

- `before.txt` is a stiff machine draft.
- `good-rewrite.txt` says the same thing in plainer words. Every fact is still there.
- `bad-rewrite.txt` reads well but changed the facts: a number, a month, a citation, a quotation, and how sure the claims are.

The good rewrite passes:

```bash
python3 scripts/ownwords check examples/before.txt examples/good-rewrite.txt
```

The bad rewrite fails, and the checker lists each thing that changed:

```bash
python3 scripts/ownwords check examples/before.txt examples/bad-rewrite.txt
```

Run both from the top folder of the project.

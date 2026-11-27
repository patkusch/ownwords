# Changelog

What changed, newest first. Nothing has been released as a numbered version yet.

## Not yet released

### 2026-11-27

- Added a plain-words step to the skill: everyday words, verbs in place of nouns, one idea per sentence.
- `ownwords score` now also says how plain a text is.
- `ownwords check` now says whether a rewrite came out plainer or heavier.
- Small slips (typos, dropped commas) are now added only when the person asks. A blind reader preferred clean rewrites 10 to 1.
- Tested plain words and human habits apart. Both kept the facts. The reader test could not judge either, because it favours shorter text.

### 2026-11-26

- First version: the skill, the fact lock, the claim lock, and the dated list of signs.
- Planted-error bench, with a gate in CI so the checker cannot get worse unnoticed.
- Two-way trial: rewrites with the skill against rewrites without it.
- Blind reader test, with a local model as the reader and a sheet for a person.
- `ownwords quirks` adds small slips and never touches a fact.
- `ownwords kept` records what a person changed in a rewrite.

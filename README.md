# ownwords

[![tests](https://github.com/patkusch/ownwords/actions/workflows/tests.yml/badge.svg)](https://github.com/patkusch/ownwords/actions/workflows/tests.yml)

**Make machine-sounding text read like a person wrote it, without changing what it says.**

Most "humanizer" tools rewrite your text and hope for the best. They change numbers, drop names, turn "may" into "will", and sometimes invent a quotation. ownwords rewrites the text and then checks its own work. If a number, name, date, quotation, link or claim changed, the rewrite fails and is fixed before you see it.

It has two parts:

- **A skill** ([SKILL.md](SKILL.md)) that tells an AI assistant how to do the rewrite.
- **A small checker** that runs on your own computer, needs nothing installed beyond Python, and sends your text nowhere.

## What it is not

ownwords does not help text get past AI detectors, and it will not. Detectors are unreliable, and the tools that chase them damage the writing. This project makes a draft clearer and more like you. If your school, employer or publisher asks you to say when you used AI, that is still yours to do.

## Try the checker

```bash
git clone https://github.com/patkusch/ownwords
```

```bash
cd ownwords
```

Compare a rewrite with the original:

```bash
python3 scripts/ownwords check examples/before.txt examples/bad-rewrite.txt
```

```text
FAIL: the rewrite changed something it must not change.
  [fail] A number is missing: 1200  (number-lost)
  [fail] A number appeared: 1300  (number-added)
  [fail] A date is missing: jun  (date-lost)
  [fail] A quotation was changed or removed: suggest a modest effect  (quote-lost)
  [fail] A word of doubt was removed, so the claim is now stronger: may, suggest  (doubt-removed)
  ...
```

See which signs of machine drafting are in a text:

```bash
python3 scripts/ownwords score examples/before.txt
```

List every sign it looks for, with its source and the date it must be checked again:

```bash
python3 scripts/ownwords tells
```

### What the result code means

A script can read the result without reading the report.

| Code | Meaning |
|---|---|
| 0 | Pass. Every fact and claim checked is still there. |
| 1 | Fail. Something that must not change has changed. |
| 2 | The command was typed wrongly, or a file could not be read. |
| 3 | Review. No fact changed, but a person should look. |

Add `--strict` to treat a review as a fail.

## Use the skill

Copy this folder to where your assistant keeps its skills. For Claude Code:

```bash
git clone https://github.com/patkusch/ownwords ~/.claude/skills/ownwords
```

Then ask it to "humanize this", "make this sound less like AI", or "what makes this read as AI?".

## What the checker catches

Each sample text was damaged in one known way, and the checker was asked whether anything changed. There are 32 sample texts: 16 machine drafts and 16 pieces of human writing from 2021.

| What was planted | Tried | Caught |
|---|---|---|
| A number changed | 31 | 31 |
| A percent sign dropped | 8 | 8 |
| A month changed | 14 | 14 |
| A name changed | 30 | 30 |
| A word changed inside a quotation | 12 | 12 |
| A link changed | 3 | 3 |
| A word of doubt removed ("may", "suggests") | 17 | 17 |
| "About" or "at least" removed from a figure | 12 | 12 |
| A "not" added or removed | 29 | 29 |
| "Definitely" or "always" added | 29 | 29 (28 as a point to review) |
| A sentence with an invented fact added | 32 | 32 |
| A sentence holding a number removed | 32 | 30 |

### What it does not catch

| What was planted | Tried | Caught |
|---|---|---|
| Two numbers swapped with each other | 30 | 11 |
| A sentence with no number or name removed | 26 | 13 |
| A vague sentence with no fact added | 32 | 0 |

The checker compares lists of facts. It does not read for meaning. So it cannot see a fact attached to the wrong thing, or a sentence that says something different using the same key words. The skill tells the assistant to read the rewrite against the original as well, for this reason. No sample held a citation, so removed citations are covered only by the unit tests.

Run it yourself:

```bash
python3 scripts/bench.py
```

## Does the skill help?

Two assistants each rewrote the same 16 machine drafts. One was told only to make the text read like a careful person wrote it. The other followed the skill. Both sets were then checked against the same originals.

| | Without the skill | With the skill |
|---|---|---|
| Rewrites with no fact or claim changed | 2 of 16 | 12 of 16 |
| Changes found by the checker | 47 | 3 |
| Words kept | 67% | 78% |

On the 8 drafts kept aside as a held-out set, the count was 1 of 8 without the skill and 7 of 8 with it.

Read these numbers with care.

- **The with-skill arm was allowed to run the checker, so it is no surprise it passes the checker.** The useful number is the other column: a capable assistant, asked plainly to humanize, changed a fact or claim in 14 of 16 drafts. Checked by hand, these included "suggests a small benefit" becoming "that is a small effect", and a shortened quotation.
- **Some of the 47 are false alarms.** The count of "not" words changes in honest edits too. Nobody has gone through all 47 by hand.
- **The checker was improved after this trial.** The first run flagged capital letters in headings and labels as lost names. That was fixed, and the numbers above come from the fixed checker on the same rewrites. So this is not a clean held-out result for the name check.
- **One trial, one run each, one model family.** No repeat runs, so no measure of run-to-run noise.
- **Keeping facts is not the same as reading better.** That is measured separately, below.

Everything from the trial is in [evals/trial](evals/trial), including the assistant's notes on where the skill got in its way.

## Does it read better?

A blind reader saw two versions of each document with no labels and picked one. Each pair was shown twice, once in each order. If the pick changed with the order, the pair counts as a tie. The reader was a local model (Gemma 3, 12B), a different model family from the one that wrote the rewrites.

| Comparison, 16 pairs each | First preferred | Second preferred | Tie |
|---|---|---|---|
| With the skill against the machine draft | 9 | 0 | 7 |
| With the skill against the rewrite without it | 2 | 1 | 13 |
| Rewrite without the skill against the machine draft | 2 | 1 | 13 |
| Habits and slips against the clean skill rewrite | 1 | 10 | 5 |
| Habits and slips against the machine draft | 4 | 4 | 8 |
| Plain words and habits against the earlier skill rewrite | 0 | 6 | 10 |
| Plain words and habits against the machine draft | 7 | 0 | 9 |
| Plain words only against the earlier skill rewrite | 0 | 7 | 9 |
| Human habits only against the earlier skill rewrite | 0 | 6 | 10 |
| Plain words only against human habits only | 0 | 4 | 12 |

What this says:

- **The skill's rewrite beat the machine draft** in 9 of 16 pairs and never lost.
- **This reader cannot separate the two rewrites.** In 13 of 16 pairs it simply picked whichever version it saw first.
- **Deliberate slips lost.** The version with misspellings and dropped commas lost to the clean rewrite 10 to 1, and only drew with the machine draft.

- **The newer skill did not beat the older one, and length is the likely reason.** The plain-words step and the human habits were tested together and then apart. Each time the first version of the skill won. But the first version cut about a quarter of the words, and every later version cut a tenth or less. Across all rewrite-against-rewrite pairs where the reader made up its mind, the shorter text won 24 times and the longer one twice. So this test cannot say whether plain words or human habits help or hurt. It says this reader likes shorter text, although it was told not to judge on length.

A small model is a poor stand-in for a person, and a model may punish typos more than a human reader would. To judge for yourself, [evals/reader/sheet.md](evals/reader/sheet.md) holds 32 unlabelled pairs:

```bash
python3 scripts/reader_test.py tally your-answers.txt
```

## Plain words

Machine drafts use heavy words and hide verbs inside nouns. The skill swaps them for everyday words, and `ownwords score` lists them with a plainer word for each. `ownwords check` says whether a rewrite came out plainer or heavier.

All 16 documents together:

| Version | Words per sentence | Long words | Heavy phrases per 1,000 words | Sentences over 30 words |
|---|---|---|---|---|
| Machine draft | 14.9 | 18.7% | 12.8 | 4 |
| Skill before this step | 12.5 | 13.1% | 4.6 | 1 |
| Skill with plain words | 12.2 | 12.6% | 1.3 | 0 |
| Rewrite without the skill | 10.6 | 4.3% | 0.0 | 0 |

A long word has nine letters or more. With the plain-words step, 13 of 16 rewrites passed the fact lock outright, and the other 3 were known false alarms. The rewrite without the skill is plainest of all, and it is also the one that changed a fact or claim in 14 of 16 drafts.

The heavy-word list is this project's own. Fewer heavy words did not make the blind reader prefer the text, as the table above shows.

## Human habits and small slips

The skill gives a rewrite the habits of someone writing by hand: contractions, uneven sentences, starting with "And" or "But". If you ask for them, it can also add a few small mistakes:

```bash
python3 scripts/ownwords quirks rewrite.txt -o final.txt
```

This adds roughly one slip per 90 words: a common misspelling, a dropped apostrophe or comma, two spaces after a full stop. It lists every slip it made. It never touches a number, name, quotation, link, citation, code, heading, or a word that says how sure a claim is, and it checks its own result against the fact lock. In the trial, 13 of 16 rewrites with habits and slips passed the lock outright, and the other 3 were false alarms of the kinds described above.

The slips are off unless you ask, because the reader test above went against them 10 to 1. When they are used, the skill lists each one and keeps a clean copy. The habits and the slips were tested together, so the habits have no reading of their own yet.

## The signs it scores, and the ones it refuses to

The scorer looks for a short list of signs. Each one has a source, the date it was added, and a date by which it must be checked again. A sign past its check date stops counting until someone confirms it still holds. Word lists go stale in about a year, so this matters.

Some popular "signs" are left out on purpose, because real people write that way: a dash on its own, good grammar, linking words such as "however", plain or formal vocabulary, a single overused word. `ownwords tells` prints the full list with reasons.

How well does the scorer do?

- **Human writing:** 1 of 16 samples showed any sign.
- **Machine drafts:** 15 of 16 showed a sign. But most of that is the chatbot's own remarks, such as "Would you like me to adjust the tone?". Looking only at the prose itself, on the 8 held-out drafts, 4 showed a sign.

So the scorer is a pointer, not a judge. It misses a lot of machine-sounding prose. The skill treats it that way.

The human samples are all Wikipedia articles from 2021, which is one style of writing. The machine drafts all come from one small local model.

## How it is allowed to change

A change to the skill or the checker ships only if every planted error caught before is still caught, no past failure returns, real writing stays unflagged, and nothing is tuned against an AI detector. The first three run automatically on every push. The full rule is in [docs/SHIP-RULE.md](docs/SHIP-RULE.md), and changes that were tried and rejected are logged in [docs/REJECTED.md](docs/REJECTED.md).

When you edit a rewrite, `ownwords kept` records which sentences you changed. Turning those records into better rules is not automatic yet.

## Not built yet

- A reader test with people. The blind sheet exists, but only a model has judged so far.
- A reader test that holds length steady, so that plain words and human habits can be judged on their own.
- Scoring a rewrite against samples of your own writing. The skill uses your samples, but nothing measures how close it got.
- Languages other than English. The fact check works on numbers, links and quotations in any language. The signs are English only.
- Repeat runs of the trial, to measure noise.

## Where the ideas came from

The signs come from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) and the studies it cites. That page warns against treating the signs as the problem to fix, and this project takes the warning seriously. The idea of fitting a checker beside a writing skill owes a debt to [slop-guard](https://github.com/eric-tramel/slop-guard), and the idea of freezing numbers and citations to [academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer). No code or text was copied from either.

## Licence

MIT for the code and the skill. The human samples in `evals/human` are excerpts from Wikipedia under CC BY-SA 4.0. Their sources are listed in [evals/human/SOURCES.md](evals/human/SOURCES.md).

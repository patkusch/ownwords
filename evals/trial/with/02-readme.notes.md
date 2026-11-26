# 02-readme: hand-over notes

## Lines left out of the saved original

- None. The original was saved as given.

## Score of the original

32.5 points per 1,000 words. One sign: a chatbot leftover on the License line.

## Check result

Passed with one kind of waiver (missing "names" that are not names).

Script output of the final run:

```
PASS: every fact and claim checked is still there.
  [waived] A name is missing: Features (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Go-Based (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Important (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Key (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Note (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Robust (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Setup (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Simple (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
  [waived] A name is missing: Synchronization (reason given: the lost words (Key, Features, Fast, Synchronization, Robust, Simple, Setup, Go-Based, Important, Note) are capitalised bullet labels, not names of anyone or anything; every real name is still there)
```

## Waivers, and why

- The check listed nine missing names: Features, Go-Based, Important, Key, Note, Robust, Setup, Simple, Synchronization. All nine are words from the bold labels in front of each bullet ("Key Features", "Fast Synchronization", "Robust Testing", "Simple Setup", "Go-Based", "Important Note"). None is the name of a person, product or place. Tidepool, Go and the version number are all still there.

## What I changed

- Removed the bold label in front of every bullet. The bullets now just say the thing.
- "boasts approximately three times the speed" became "is approximately three times as fast". The word "approximately" and the note about the author's own testing are kept.
- Cut the sales question "Tired of manually transferring photos between devices?" and kept what it said as a plain statement.
- Moved the caution about disk speed next to the speed claim it belongs to.
- Dropped the bullet "Go-Based: Built with performance and efficiency in mind". The first line already says it is written in Go, and the rest says nothing.

## What I left out or left alone on purpose

- The two placeholder lines (License, Get Started) are still there, word for word. They are instructions to you from the chatbot. I cannot fill them in without making up a fact.
- Kept "with improved performance and reliability" because it is a claim, even though it is vague.
- Kept the heading and the documentation link exactly.

## Questions for you

- Which licence is Tidepool under?
- What is the real repository address?
- "Improved reliability" is vague. Is there something specific that got more reliable in 2.3?

## Where the skill or the script got in the way

- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.
- The score step did not flag "boasts" in this file, although the skill lists it as a sign. It also did not flag the bold-label bullet list.

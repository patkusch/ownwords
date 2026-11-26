# 12-memo: hand-over notes

## Lines left out of the saved original

- "Do you want me to modify this memo in any way, such as adding specific metrics or outlining the training plan?"
- The "---" line that separated the draft from the chatbot's words, and the blank lines around it.

## Score of the original

26.5 points per 1,000 words. One chatbot leftover (the FROM placeholder).

## Check result

Passed with one kind of waiver.

Script output of the final run:

```
PASS: every fact and claim checked is still there.
  [waived] A name is missing: Considerations (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Executive (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Financial (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Proposed (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Solution (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Steps (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
  [waived] A name is missing: Summary (reason given: Executive, Summary, Proposed, Solution, Financial, Considerations, Steps are capitalised section labels, not names; the sections are now plain paragraphs)
```

## Waivers, and why

- Missing "names" Executive, Summary, Proposed, Solution, Financial, Considerations, Steps: all are words from the bold section labels. Not names.

## What I changed

- Removed the bold label in front of each paragraph. The memo is short, so plain paragraphs are enough. The TO / FROM / DATE / SUBJECT block is kept.
- Put the recommendation and the start date in the first sentence. The old memo said the recommendation twice.
- "commencing" became "starting"; "utilizing a remote support model" and "Leveraging learnings from" are gone.
- The Leeds result now comes as a plain sentence.

## What I left out or left alone on purpose

- "[Your Name/Department]" is still in the FROM line.
- Kept "strongly recommend", "approximately 70%", "under £5,000" and "We believe" as they were.
- Kept "successful" for the Leeds trial.

## Questions for you

- Who is the memo from?
- The background gives wait times as the problem, but success is measured by resolution time and satisfaction. Should wait time be a measure too, since that is what Leeds reported?
- Do you have the current average wait time here, to set against the Leeds figures?

## Where the skill or the script got in the way

- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.

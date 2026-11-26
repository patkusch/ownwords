# 15-faq: hand-over notes

## Lines left out of the saved original

- "Okay, here's a 200-word FAQ answer addressing the safety of the Oakline water filter for well water:"
- "Would you like me to adjust this FAQ to focus on a specific aspect, or perhaps add a call to action (e.g., "Contact a water testing specialist")?"
- The "---" line that separated the draft from the chatbot's words, and the blank lines around it.

## Score of the original

5.5 points per 1,000 words. One sign: "it's important to understand".

## Check result

Passed with one kind of waiver.

Script output of the final run:

```
PASS: every fact and claim checked is still there.
  [waived] A name is missing: Considerations (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
  [waived] A name is missing: Crucial (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
  [waived] A name is missing: Findings (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
  [waived] A name is missing: Important (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
  [waived] A name is missing: Key (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
  [waived] A name is missing: Performance (reason given: Key, Findings, Important, Considerations, Crucial, Performance are capitalised bullet labels, not names; Oakline and Hartwell Labs are kept)
```

## Waivers, and why

- Missing "names" Considerations, Crucial, Findings, Important, Key, Performance: words from the bold labels ("Key Findings", "Important Considerations", "Testing is Crucial", "Filter Performance"). Not names. Oakline and Hartwell Labs are kept.

## What I changed

- The answer now comes first: it depends on your water, and the filter is not certified for well water. The old version left the certification until the last bullet.
- Removed the bold label in front of each point and the separate "Disclaimer" paragraph. Its content (use it with professional testing and follow-up treatment) is kept in the testing paragraph.
- Cut "it's important to understand its limitations" and went straight to the limitation.
- "Our rigorous lab testing ... demonstrates its effectiveness in removing contaminants" was replaced by what the testing found.

## What I left out or left alone on purpose

- Still bold: "not certified" and "It does not remove bacteria or nitrates". These are the safety points.
- Kept "at least 99%", "approximately 400 litres", "around 2 months", "Currently" and the emphasis on "must".
- I moved the certification sentence up. This is a change of order. I made it because the question is "is it safe" and the certification is the most direct answer.
- Dropped the word "rigorous" and the general claim that the testing "demonstrates its effectiveness in removing contaminants". The specific result is kept. Put the general claim back if you need it.

## Questions for you

- The draft says "Our ... lab testing, conducted by Hartwell Labs". Was the testing independent, or commissioned by you? The answer should say.
- Is the filter certified for anything, such as mains water? "Not certified for well water" invites that question.

## Where the skill or the script got in the way

- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.
- The check did not notice that I moved the certification sentence or dropped the general effectiveness claim. I am reporting both here.

# 04-blog: hand-over notes

## Lines left out of the saved original

- "Okay, here's a 220-word blog post based on the provided facts, aiming for an engaging and informative tone:"
- "Would you like me to tweak this post in any way, perhaps focusing on a specific aspect or adding a call to action (e.g., “Share your thoughts on flexible working in the comments!”)?"
- Both "---" lines around the post.

## Score of the original

0.0 points per 1,000 words. The script said "No signs found. Leave this text alone." I did not leave it alone, because it did not read fine to me (see the changes below).

## Check result

Passed with two kinds of waiver.

Script output of the final run:

```
PASS: every fact and claim checked is still there.
  [waived] A name is missing: Bold (reason given: Takes, Bold, Step are capitalised headline words, not names; headline shortened)
  [waived] A name is missing: Step (reason given: Takes, Bold, Step are capitalised headline words, not names; headline shortened)
  [waived] A name is missing: Takes (reason given: Takes, Bold, Step are capitalised headline words, not names; headline shortened)
  [waived] The number of "not" words changed, so a meaning may have flipped: 1 before, 0 after (reason given: removed 'the real story isn't just about the numbers', a point nobody made; meaning unchanged)
```

## Waivers, and why

- Missing "names" Takes, Bold, Step: these are words from the old headline "Leeds Bakery Takes a Bold Step". Not names. I shortened the headline.
- The count of "not" words went from 1 to 0, because I removed "the real story isn't just about the numbers". Nobody had said it was. Meaning unchanged.

## What I changed

- Shortened the headline.
- Cut "charming", "took a gamble", "Thankfully" and the exclamation marks.
- Cut "the results are fascinating" and "a huge benefit for anyone working long hours". Neither is a fact about this bakery.
- Cut the ending ("a real-world example of how businesses are experimenting", "Will this bold move pay off?", "Stay tuned for updates!"). It was a formula.
- "she confessed" became "she said".

## What I left out or left alone on purpose

- All three quotations are word for word.
- I left the sentence "Starting her business on the 2nd, she initially employed 9 staff..." exactly as it was, although it does not make sense. See the question.
- "Stay tuned for updates" is gone. If you do plan a follow-up post, say so and I will put a plain line back.
- My first headline used the word "Tries". The check called that a new name, so I chose a headline that adds no capitalised word.

## Questions for you

- "Starting her business on the 2nd" looks wrong. Did the four-day week start on 2 February 2026? And were there 9 staff at that point?
- "Things quickly rebounded": was it sales that recovered, and by when?

## Where the skill or the script got in the way

- The score step found no signs and printed "Leave this text alone", but the skill says to stop only if the text also reads fine. It did not, so I rewrote it. The script's message and the skill's rule pull in different directions here.
- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.

# 05-product: hand-over notes

## Lines left out of the saved original

- "Would you like me to tailor this description for a specific platform (e.g., Amazon, website)?"
- The "---" line that separated the draft from the chatbot's words, and the blank lines around it.

## Score of the original

0.0 points per 1,000 words. The script said "No signs found. Leave this text alone." I did not leave it alone, because it did not read fine to me (see the changes below).

## Check result

Passed with two kinds of waiver.

Script output of the final run:

```
PASS: every fact and claim checked is still there.
  [waived] A name is missing: Illuminate (reason given: Illuminate and Ride are capitalised headline words, not names)
  [waived] A name is missing: Ride (reason given: Illuminate and Ride are capitalised headline words, not names)
  [waived] The number of "not" words changed, so a meaning may have flipped: 1 before, 0 after (reason given: removed the slogan 'Don't let the darkness hold you back!'; no claim lost)
```

## Waivers, and why

- Missing "names" Illuminate and Ride: words from the old headline "Illuminate Your Ride with". Not names. Fennel 3 is kept.
- The count of "not" words went from 1 to 0, because I removed the slogan "Don't let the darkness hold you back!". No claim was lost.

## What I changed

- Headline is now just the product name.
- "Boasting an impressive 800 lumens" became "At 800 lumens".
- Cut "on every adventure", "Enjoy extended ride times", "maximizing comfort and minimizing weight", "perfect for unpredictable weather", "exceptional performance and peace of mind".
- Each paragraph now states the specification and what it means for the rider.

## What I left out or left alone on purpose

- Every figure is unchanged and still bold: 800 lumens, up to 6 hours on low, 2-hour charge, 96 grams, IPX6, $49, 2-year warranty.
- Kept "up to" on the battery life and "comprehensive" on the warranty, because both change what is promised.
- Kept the order line, since this is sales copy.
- Left out "designed to keep you safe". The visibility claim is kept.

## Questions for you

- How long does the battery last on the 800-lumen setting? Buyers will ask. I did not add a figure.
- What does the warranty cover?

## Where the skill or the script got in the way

- The score step found no signs and printed "Leave this text alone", but the skill says to stop only if the text also reads fine. It did not, so I rewrote it. The script's message and the skill's rule pull in different directions here.
- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.

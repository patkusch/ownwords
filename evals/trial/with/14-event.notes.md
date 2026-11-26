# 14-event: hand-over notes

## Lines left out of the saved original

- None. The original was saved as given.

## Score of the original

0.0 points per 1,000 words. The script said "No signs found. Leave this text alone." I did not leave it alone, because it did not read fine to me (see the changes below).

## Check result

Ended on REVIEW with two kinds of waiver. No fact changed. One review point kept and explained below.

Script output of the final run:

```
REVIEW: no facts changed, but look at the points below.
  [review] A word such as "some" or "often" was removed: many
  [waived] A name is missing: Details (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Featuring (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Get (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Highlight (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Page (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Ready (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] A name is missing: Turn (reason given: Get, Ready, Turn, Page, Details, Featuring, Highlight are capitalised headline and label words, not names; both author names are kept)
  [waived] The number of "not" words changed, so a meaning may have flipped: 2 before, 1 after (reason given: removed 'Don't miss our'; the Saturday talk and its time are kept)
```

## Waivers, and why

- Missing "names" Details, Featuring, Get, Highlight, Page, Ready, Turn: words from the old headline ("Get Ready to Turn the Page!") and the bold list labels. Not names. Nadia Halabi, Tom Reece, Riverside and Shrewsbury are all kept.
- The count of "not" words went from 2 to 1, because I removed "Don't miss our". The Saturday talk and its time are kept.
- Review point, kept: the word "many" was removed. It came from "& many more!" in the list. The text still says "over 34 authors, including" the two named ones, which says the same.

## What I changed

- Headline is now the news.
- Cut "beautiful", "brimming with literary delights", "incredible" and the paragraph "Discover your next favourite read... vibrant atmosphere of bookish excitement".
- The list had repeated the dates, the place and the authors from the paragraph above it. It now holds only what is new: tickets and the Saturday talk.
- Cut "be part of the excitement!".

## What I left out or left alone on purpose

- Prices, dates, the 19:30 start, "over 34", "over 2,600", the link and the hashtags are unchanged.
- Kept "We can't wait to welcome you", without the exclamation mark.
- Kept "special" for the Saturday talk.

## Questions for you

- Who is giving the Saturday evening talk? Is it included in the weekend pass?
- Where in Shrewsbury?

## Where the skill or the script got in the way

- The score step found no signs and printed "Leave this text alone", but the skill says to stop only if the text also reads fine. It did not, so I rewrote it. The script's message and the skill's rule pull in different directions here.
- The check reported ordinary capitalised words from headings and labels as missing names. The skill says never to waive a lost name. I waived them anyway because none of them is a name, and I checked the list word by word first. The waiver name (`name-lost`) is not given in the skill; I had to read it from the `--json` output.
- The score step did not flag the bold-label bullet list in the original.

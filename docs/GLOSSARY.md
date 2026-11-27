# Words this project uses

| Word | What it means here |
|---|---|
| Skill | A set of written instructions an AI assistant follows. Here it is [SKILL.md](../SKILL.md). |
| Checker | The small program that compares a rewrite with the original. |
| Lock | The check that fails a rewrite if something that must stay the same has changed. |
| Fact lock | The part that looks at numbers, dates, times, links, email addresses, citations, quotations and names. |
| Claim lock | The part that looks at how sure a claim is: words such as "may", "about", "often" and "not". |
| Sign | A pattern that often shows up in machine drafts, such as "it is important to note". |
| Check date | The day a sign must be looked at again. After that day it is no longer scored. |
| Finding | One thing the checker noticed, such as "a number is missing". |
| Waiver | Accepting one kind of finding as a false alarm, with a stated reason. The reason is printed in the report. |
| False alarm | The checker failed a rewrite that changed nothing in meaning. |
| Blind spot | A kind of change the checker is known to miss. They are listed in the README. |
| Slip | A small mistake added on purpose, such as a typo. Only added when asked for. |
| Human habit | A way people really write, such as contractions and uneven sentences. |
| Heavy word | A long or formal word with an everyday word that says the same thing. |
| Planted error | Damage done to a sample text on purpose, to see whether the checker notices. |
| Bench | The run that plants every kind of error and counts how many are caught. |
| Trial | The same drafts rewritten in different ways, so the ways can be compared. |
| Held-out drafts | Drafts that are scored but never read while writing a rule. |
| Blind reader test | A reader sees two versions with no labels and picks one. |
| Ship rule | The conditions a change must meet before it goes in. See [SHIP-RULE.md](SHIP-RULE.md). |

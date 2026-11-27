# Questions people ask

**Will this get my text past an AI detector?**
No. It is not built for that and is never tuned against a detector.

**Does my text leave my computer?**
The checker sends nothing anywhere. It reads the two files and prints a report. The rewrite itself is done by whichever AI assistant you use, under that assistant's own terms.

**What do I need to install?**
Python 3.10 or newer. Nothing else.

**Can I use the checker without the skill?**
Yes. Give it any original and any rewrite, whoever or whatever wrote them.

**The checker failed my rewrite, but the meaning is the same. What now?**
That is a false alarm. Run the check again with `--waive` and a reason. The reason is printed in the report, so nothing is hidden. Please also open an issue so the false alarm can be fixed.

**The checker passed a rewrite that changed something. How?**
It compares key items, not meaning. It misses two numbers swapped with each other, and a fact moved onto the wrong subject. The README lists what it misses and how often. Read the rewrite once yourself.

**Does it work in other languages?**
Partly. Numbers, links and quotations are checked in any language. The signs of machine drafting are English only.

**Will the rewrite be shorter?**
Usually. Sentences that say nothing are cut. Nothing that carries a fact is cut.

**Can it add typos so the text looks more human?**
Only if you ask. In a blind test, a reader preferred the clean version 10 times and the version with slips once.

**Why do the signs have dates?**
The words machines overuse change from year to year. Each sign has a day it must be checked again. After that day it is no longer scored.

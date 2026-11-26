import datetime
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ownwords import claims, facts, plain, quirks, tells  # noqa: E402
from ownwords.cli import check  # noqa: E402


def kinds(before, after):
    return {f["kind"] for f in check(before, after)["fail"] + check(before, after)["review"]}


class Facts(unittest.TestCase):
    def test_numbers_normalise(self):
        got = facts.extract("It cost $1,200, up 3.50% on 3 million users and twelve sites.")["number"]
        self.assertEqual(got, {"1200$", "3.5%", "3000000", "12"})

    def test_number_inside_link_is_not_a_number(self):
        got = facts.extract("See https://example.org/v2/report-2024.pdf for more.")
        self.assertEqual(got["number"], set())
        self.assertEqual(got["link"], {"https://example.org/v2/report-2024.pdf"})

    def test_link_drops_trailing_full_stop(self):
        self.assertEqual(facts.extract("Go to https://a.example/x.")["link"], {"https://a.example/x"})

    def test_dates_and_times(self):
        got = facts.extract("We met on Tuesday 3 March 2025 at 10:30am, then on 2026-01-09.")
        self.assertEqual(got["date"], {"tuesday", "mar", "2026-01-09"})
        self.assertEqual(got["time"], {"10:30am"})

    def test_may_the_month(self):
        self.assertIn("may", facts.extract("It opens in May 2026.")["date"])
        self.assertNotIn("may", facts.extract("It may open soon.")["date"])

    def test_names_skip_sentence_starts(self):
        got = facts.extract("Yesterday the board met. Results were sent to Priya Raman at NASA.")["name"]
        self.assertEqual(got, {"Priya", "Raman", "NASA"})

    def test_two_word_name_at_sentence_start(self):
        self.assertIn("Marta", facts.extract("Marta Kowalczyk runs the bakery.")["name"])

    def test_name_with_possessive_is_still_there(self):
        self.assertEqual(facts.compare("We asked Fatima Noor.", "We took Fatima Noor's advice."), [])

    def test_heading_and_label_capitals_are_not_names(self):
        before = "**Key Features:**\n\nSubject: Update On Boiler Issues\n\nThe tool is fast."
        self.assertEqual(facts.extract(before)["name"], set())

    def test_sign_off_name_counts(self):
        self.assertEqual(facts.extract("Thanks for reading.\n\nPriya Raman")["name"], {"Priya", "Raman"})

    def test_citations(self):
        got = facts.extract("This is known [3, 4] and was repeated (Chen and Abara, 2024).")["citation"]
        self.assertEqual(got, {"[3,4]", "(Chen and Abara 2024)"})

    def test_one_as_word_or_digit(self):
        self.assertEqual(facts.compare("There was 1 delay.", "There was one delay."), [])

    def test_lost_and_added(self):
        found = {f["kind"] for f in facts.compare("Paid £40 to Kessler on 3 March.", "Paid £45 to Kesler on 3 April.")}
        self.assertEqual(found, {"number-lost", "number-added", "name-lost", "name-added",
                                 "date-lost", "date-added"})


class Claims(unittest.TestCase):
    def test_same_text_is_clean(self):
        text = "It may help some people, but about 40 did not respond."
        self.assertEqual(claims.compare(text, text), [])

    def test_swapping_one_doubt_word_for_another_is_fine(self):
        self.assertEqual(claims.compare("It might rain.", "It may rain."), [])

    def test_doubt_removed(self):
        self.assertIn("doubt-removed", kinds("It may rain today.", "It will rain today."))

    def test_certainty_alone_is_a_review_point(self):
        result = check("The plan is sound.", "The plan is definitely sound.")
        self.assertEqual(result["verdict"], "review")

    def test_negation(self):
        self.assertIn("negation-changed", kinds("The test was passed.", "The test was not passed."))

    def test_the_most_is_not_a_count(self):
        self.assertEqual(claims.compare("It was the most useful change.", "It was a useful change."), [])
        self.assertIn("how-often-removed", kinds("Most staff agreed.", "Staff agreed."))

    def test_about_only_counts_before_a_figure(self):
        self.assertEqual(claims.compare("We talked about pricing.", "We discussed pricing."), [])

    def test_text_halved(self):
        long = " ".join(["The committee reviewed the plan in detail and agreed it."] * 6)
        self.assertIn("text-halved", kinds(long, "The committee agreed the plan."))


class Tells(unittest.TestCase):
    def test_clean_text_scores_zero(self):
        self.assertEqual(tells.score("The boiler broke on Monday. We fixed it on Friday.")["points"], 0)

    def test_one_overused_word_is_not_a_sign(self):
        self.assertEqual(tells.score("This is a crucial step.")["found"], [])

    def test_three_overused_words_are(self):
        found = tells.score("A pivotal, vibrant tapestry of crucial ideas.")["found"]
        self.assertEqual([f["id"] for f in found], ["word-cluster"])

    def test_dash_alone_is_not_a_sign(self):
        self.assertEqual(tells.score("It rained — hard — all week.")["found"], [])

    def test_signs(self):
        text = ("Certainly! Here is a draft. The town stands as a testament to resilience, "
                "highlighting its enduring legacy. It's not just a town, it's a community. "
                "Experts say it will thrive.")
        ids = {f["id"] for f in tells.score(text)["found"]}
        self.assertTrue({"chatbot-leftover", "inflated-importance", "trailing-ing",
                         "not-just-but", "vague-source"} <= ids)

    def test_sign_past_its_check_date_is_not_scored(self):
        text = "It's not just a town, it's a community."
        late = tells.score(text, today=datetime.date(2030, 1, 1))
        self.assertEqual(late["points"], 0)
        self.assertIn("not-just-but", late["stale_not_scored"])

    def test_every_sign_has_a_source_and_dates(self):
        for tell in tells.load()["tells"]:
            self.assertTrue(tell["source"].startswith("https://"), tell["id"])
            self.assertLess(datetime.date.fromisoformat(tell["added"]),
                            datetime.date.fromisoformat(tell["review_by"]), tell["id"])
            self.assertIn(tell["evidence"], {"certain", "measured", "catalogue"})


class Plain(unittest.TestCase):
    HEAVY = ("In order to facilitate the implementation of the new system, the team conducted an "
             "analysis of the requirements prior to the commencement of work.")
    LIGHT = "The team studied what the new system needed before they started work."

    def test_heavy_words_are_found_with_a_plainer_word(self):
        found = {h["text"].lower(): h["plainer"] for h in plain.measure(self.HEAVY)["heavy_words"]}
        self.assertEqual(found["in order to"], "to")
        self.assertEqual(found["prior to"], "before")
        self.assertIn("facilitate", found)

    def test_hidden_verbs_are_found(self):
        phrases = [p["text"].lower() for p in plain.measure(self.HEAVY)["noun_heavy_phrases"]]
        self.assertIn("conducted an analysis", phrases)

    def test_plain_text_is_clean(self):
        m = plain.measure(self.LIGHT)
        self.assertEqual(m["heavy_words"] + m["noun_heavy_phrases"], [])

    def test_compare_says_plainer(self):
        notes = plain.compare(self.HEAVY, self.LIGHT)
        self.assertTrue(notes and all(n.startswith("plainer") for n in notes), notes)
        self.assertTrue(all(n.startswith("heavier") for n in plain.compare(self.LIGHT, self.HEAVY)))

    def test_quotations_are_not_judged(self):
        self.assertEqual(plain.measure('She said "we will utilize it in order to win".')["heavy_words"], [])

    def test_no_plainer_word_changes_how_sure_a_claim_is(self):
        for heavy, simple in plain.HEAVY.items():
            before, after = f"The team will {heavy} it.", f"The team will {simple} it."
            findings = [f for f in claims.compare(before, after) if f["level"] == "fail"]
            self.assertEqual(findings, [], (heavy, simple))


class Quirks(unittest.TestCase):
    TEXT = ("However, the pilot ran from 3 March 2025 across 12 clinics, and it's fair to say "
            "the staff liked it. Dr. Amara Osei said the results \"suggest that the effect is real\" "
            "and that waits may fall by about 15%. I think the team did well because the plan was "
            "simple. See https://example.org/the-report for the full story.")

    def test_slips_are_added_and_listed(self):
        changed, notes = quirks.add(self.TEXT, seed=1, every=20)
        self.assertNotEqual(changed, self.TEXT)
        self.assertGreaterEqual(len(notes), 2)

    def test_one_common_word_is_not_misspelled_every_time(self):
        text = "We went to the shop and the park and the pool with the dog because the sun was out. " * 6
        _, notes = quirks.add(text, seed=4, every=10)
        spelled = [n for n in notes if "spelled" in n]
        self.assertLessEqual(sum('"the"' in n for n in spelled), 1)

    def test_same_seed_same_result(self):
        self.assertEqual(quirks.add(self.TEXT, seed=3), quirks.add(self.TEXT, seed=3))

    def test_facts_and_claims_survive_every_seed(self):
        for seed in range(40):
            changed, _ = quirks.add(self.TEXT, seed=seed, every=10)
            self.assertEqual(check(self.TEXT, changed)["verdict"], "pass", (seed, changed))
            for kept in ("3 March 2025", "12 clinics", "Dr. Amara Osei", "about 15%", "may fall",
                         "\"suggest that the effect is real\"", "https://example.org/the-report"):
                self.assertIn(kept, changed, seed)

    def test_real_rewrites_still_pass_the_lock(self):
        for path in sorted((ROOT / "evals" / "trial" / "with").glob("[0-9]*.txt")):
            if path.name.endswith(".original.txt"):
                continue
            text = path.read_text(encoding="utf-8")
            for seed in range(5):
                changed, _ = quirks.add(text, seed=seed, every=40)
                self.assertEqual(check(text, changed)["verdict"], "pass", (path.name, seed))


class Regressions(unittest.TestCase):
    def test_every_past_failure(self):
        cases = json.loads((ROOT / "evals" / "regressions" / "cases.json").read_text())
        self.assertGreaterEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case["name"]):
                result = check(case["before"], case["after"])
                if case["expect"] == "pass":
                    self.assertEqual(result["verdict"], "pass", result)
                else:
                    self.assertEqual(result["verdict"], "fail", result)
                    found = {f["kind"] for f in result["fail"]}
                    self.assertTrue(set(case["kinds"]) <= found, found)


class CommandLine(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "ownwords"), *args],
                              capture_output=True, text=True)

    def setUp(self):
        import tempfile
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "a.txt").write_text("It is not just a tool, but a platform used by 40 teams.")
        (self.dir / "good.txt").write_text("It is a tool and a platform used by 40 teams.")
        (self.dir / "bad.txt").write_text("It is a platform used by 50 teams.")

    def test_exit_codes(self):
        a, good, bad = (str(self.dir / n) for n in ("a.txt", "good.txt", "bad.txt"))
        self.assertEqual(self.run_cli("check", a, good).returncode, 0)
        self.assertEqual(self.run_cli("check", a, bad).returncode, 1)
        self.assertEqual(self.run_cli("check", a, str(self.dir / "missing.txt")).returncode, 2)

    def test_waiver_needs_a_reason_and_is_shown(self):
        a, bad = str(self.dir / "a.txt"), str(self.dir / "bad.txt")
        self.assertEqual(self.run_cli("check", a, bad, "--waive", "number-lost=").returncode, 2)
        done = self.run_cli("check", a, bad, "--waive", "number-lost=typo in source",
                            "--waive", "number-added=typo in source")
        self.assertIn("reason given: typo in source", done.stdout)

    def test_score_fail_over(self):
        a = str(self.dir / "a.txt")
        self.assertEqual(self.run_cli("score", a).returncode, 0)
        self.assertEqual(self.run_cli("score", a, "--fail-over", "5").returncode, 1)

    def test_kept_records_what_the_person_changed(self):
        (self.dir / "final.txt").write_text("It is a tool used by 40 teams.")
        log = self.dir / "log" / "kept.jsonl"
        done = self.run_cli("kept", str(self.dir / "good.txt"), str(self.dir / "final.txt"), "--log", str(log))
        self.assertEqual(done.returncode, 0)
        record = json.loads(log.read_text().splitlines()[0])
        self.assertEqual(record["sentences_changed"], 1)
        self.assertEqual(record["added"], ["It is a tool used by 40 teams."])

    def test_json(self):
        a, bad = str(self.dir / "a.txt"), str(self.dir / "bad.txt")
        self.assertEqual(json.loads(self.run_cli("check", a, bad, "--json").stdout)["verdict"], "fail")
        self.assertIn("do_not_enforce", json.loads(self.run_cli("tells", "--json").stdout))


if __name__ == "__main__":
    unittest.main()

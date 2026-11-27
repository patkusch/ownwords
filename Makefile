.PHONY: test bench check

# Run everything CI runs.
check: test bench

test:
	python3 -m unittest discover -s tests

bench:
	python3 scripts/bench.py --gate

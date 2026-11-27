.PHONY: help check test bench

help:
	@echo "make check   run everything CI runs"
	@echo "make test    run the tests"
	@echo "make bench   check that every planted error is still caught"

check: test bench

test:
	python3 -m unittest discover -s tests

bench:
	python3 scripts/bench.py --gate

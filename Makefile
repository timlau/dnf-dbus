TESTLIBS=src/:test:/

run-tests:
	@PYTHONPATH=$(TESTLIBS) python3 -m unittest -v test/*.py


PNONY: run-tests


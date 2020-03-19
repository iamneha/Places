.PHONY: install test

install:
	pip install -r requirements.txt

test-install: install
	pip install -r test-requirements.txt

test: test-install
	pytest -s -v tests

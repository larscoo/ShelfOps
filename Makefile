.PHONY: help run test cov lint fmt build

PYTHON ?= .venv/bin/python

help:
	@echo "run: local server on port 8000 | test: pytest | cov: coverage >= 80%"
	@echo "lint: Ruff checks | fmt: format Python | build: wheel and sdist"

run:
	$(PYTHON) -m flask --app wsgi run --debug --host 127.0.0.1 --port 8000

test:
	$(PYTHON) -m pytest

cov:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

fmt:
	$(PYTHON) -m ruff format .

build:
	$(PYTHON) -m build

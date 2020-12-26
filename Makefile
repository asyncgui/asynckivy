PYTHON = python
PYTEST = $(PYTHON) -m pytest
FLAKE8 = $(PYTHON) -m flake8

test:
	$(PYTEST) ./tests

style:
	$(FLAKE8) --count --select=E9,F63,F7,F82 --show-source --statistics ./tests ./asynckivy ./examples
	$(FLAKE8) --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics ./asynckivy ./examples

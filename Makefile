PYTHON = python
PYTEST = $(PYTHON) -m pytest

test:
	$(PYTEST) ./tests

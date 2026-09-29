test:
	env KCFG_GRAPHICS_MAXFPS=0 python -m pytest ./tests

style:
	ruff check ./tests ./src ./examples

html:
	sphinx-build -b html ./sphinx ./docs

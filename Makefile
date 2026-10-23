test:
	env KCFG_GRAPHICS_MAXFPS=0 python -m pytest ./tests

style:
	ruff check ./tests ./src ./examples

html:
	sphinx-build -b html ./sphinx ./docs

html_commit:
	sed --in-place '\|^/docs/$$|d' ./.gitignore
	git add ./.gitignore ./docs/* ./docs/.*
	git commit -m "Generate HTML"


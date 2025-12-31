.PHONY: install format lint typecheck test check docs docs-serve docs-build build publish

install:
	uv sync --group dev

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run ty check src/layercode_create_app tests

test:
	uv run pytest

check: format lint typecheck test

docs-install:
	uv sync --group docs

docs-serve:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build

docs: docs-install docs-serve

build:
	rm -rf dist/
	uv build

publish: build
	uv publish

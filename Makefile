.PHONY: install test lint check infra-validate pipeline

install:
	pip install -e ".[dev,aws]"

test:
	pytest -q

lint:
	ruff check .

check: lint test

infra-validate:
	cd infra/terraform && terraform fmt -check -recursive && terraform init -backend=false && terraform validate

pipeline:
	python scripts/create_pipeline.py

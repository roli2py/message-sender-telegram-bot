.PHONY: all format test
all: format test

format:
	isort .
	black .

test:
	pytest

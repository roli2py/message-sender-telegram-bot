.PHONY: all typecheck format test
all: typecheck format test

typecheck:
	basedpyright

format:
	isort .
	black .

test:
	pytest --cov=src/message_sender_telegram_bot/libs

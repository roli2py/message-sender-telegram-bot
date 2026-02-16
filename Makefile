.PHONY: all typecheck format test
all: typecheck format test

typecheck:
	ty check

format:
	ruff format

test:
	pytest --cov=src/message_sender_telegram_bot/libs

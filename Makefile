.PHONY: all format test
all: format test

format:
	isort .
	black .

test:
	pytest --cov=src/message_sender_telegram_bot/libs

FROM docker.io/python:3.14.3-trixie@sha256:dae380cbff69335514b37adbf4d30d143d230f155caf752051c99a3d8133da4b

RUN useradd -m -s /bin/nologin bot
RUN --mount=type=bind,target=/mstb pip install /mstb
USER bot

CMD [ "python", "-m", "message_sender_telegram_bot.main" ]

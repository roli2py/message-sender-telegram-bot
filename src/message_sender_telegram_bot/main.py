from __future__ import annotations

from os import environ
from smtplib import SMTP
from typing import TYPE_CHECKING

from telegram import Message, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

from libs import EmailSender, GmailSMTPCreator

if TYPE_CHECKING:
    from smtplib import SMTP

    from telegram import Message

# Data from the environment variables
TELEGRAM_TOKEN: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_TELEGRAM_TOKEN"]
GMAIL_SMTP_LOGIN: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_GMAIL_SMTP_LOGIN"]
GMAIL_SMTP_PASSWORD: str = environ[
    "MESSAGE_SENDER_TELEGRAM_BOT_GMAIL_SMTP_PASSWORD"
]
EMAIL_FROM_ADDR: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_EMAIL_FROM_ADDR"]
EMAIL_TO_ADDR: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_EMAIL_TO_ADDR"]

# Creating a SMTP connection and passing to an email sender
smtp: SMTP = GmailSMTPCreator(GMAIL_SMTP_LOGIN, GMAIL_SMTP_PASSWORD).create()
email_sender: EmailSender = EmailSender(
    smtp,
    EMAIL_FROM_ADDR,
    EMAIL_TO_ADDR,
)


# Handler that pass the message to the senders
async def send(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message | None = update.effective_message

    if message is not None:
        message_text: str | None = message.text

        if message_text is not None:
            email_sender.send(message_text)


# Creating an app and adding handlers
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# TODO replace the message handle to a command handler
message_handler = MessageHandler(filters.TEXT, send)

app.add_handler(message_handler)

if __name__ == "__main__":
    app.run_polling()

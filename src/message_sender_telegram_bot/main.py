from __future__ import annotations

from os import environ
from smtplib import SMTP
from typing import TYPE_CHECKING

import telegram
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import libs

if TYPE_CHECKING:
    from smtplib import SMTP

    from sqlalchemy import Engine
    from sqlalchemy.orm import Session

# Data from the environment variables
TELEGRAM_TOKEN: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_TELEGRAM_TOKEN"]
DB_USER: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_DB_USER"]
DB_PASSWORD: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_DB_PASSWORD"]
DB_HOST: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_DB_HOST"]
DB_PORT: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_DB_PORT"]
DB_NAME: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_DB_NAME"]
GMAIL_SMTP_LOGIN: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_GMAIL_SMTP_LOGIN"]
GMAIL_SMTP_PASSWORD: str = environ[
    "MESSAGE_SENDER_TELEGRAM_BOT_GMAIL_SMTP_PASSWORD"
]
EMAIL_FROM_ADDR: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_EMAIL_FROM_ADDR"]
EMAIL_TO_ADDR: str = environ["MESSAGE_SENDER_TELEGRAM_BOT_EMAIL_TO_ADDR"]

database_engine: Engine = create_engine(
    f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True,
)
compiled_session: sessionmaker[Session] = sessionmaker(database_engine)

# Creating a SMTP connection and passing to an email sender
smtp: SMTP = libs.GmailSMTPCreator(
    GMAIL_SMTP_LOGIN, GMAIL_SMTP_PASSWORD
).create()
email_sender: libs.EmailSender = libs.EmailSender(
    smtp,
    EMAIL_FROM_ADDR,
    EMAIL_TO_ADDR,
)

# TODO make an admin panel to generate the tokens


# Handler that authorize a user
async def start(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat
    user: telegram.User | None = update.effective_user

    if chat is None or user is None:
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session, user_id=user.id
        ).get()

    if not isinstance(db_user, libs.User):
        with compiled_session() as session:
            new_db_user: libs.User = libs.DBUserManipulator(
                session, user_id=user.id
            ).create()
            session.add(new_db_user)
            session.commit()

        _ = await chat.send_message("Enter the token")

        return

    with compiled_session() as session:
        session.add(db_user)
        is_user_authorizing: bool = libs.DBUserManipulator(
            session, db_user=db_user
        ).get_authorizing_status()

    if is_user_authorizing:
        _ = await chat.send_message("Enter the token")
        return

    with compiled_session() as session:
        session.add(db_user)
        token: str | None = libs.DBUserManipulator(
            session, db_user=db_user
        ).get_token()

    if not isinstance(token, str):
        with compiled_session() as session:
            session.add(db_user)
            libs.DBUserManipulator(
                session, db_user=db_user
            ).set_authorizing_status(True)
            session.commit()

        _ = await chat.send_message(
            "Your token is expired. Please, enter a new token"
        )
        return

    with compiled_session() as session:
        valid_token: libs.ValidToken | None = libs.DBValidTokenGetter(
            session, token
        ).get()

    if not isinstance(valid_token, libs.ValidToken):
        with compiled_session() as session:
            session.add(db_user)
            db_user_manipulator: libs.DBUserManipulator = (
                libs.DBUserManipulator(session, db_user=db_user)
            )
            db_user_manipulator.clear_token()
            db_user_manipulator.set_authorizing_status(True)
            session.commit()

        _ = await chat.send_message(
            "Your token is expired. Please, enter a new token"
        )

    _ = await chat.send_message("You're already authorized")


# TODO make a confirmation of a message send
# Handler that pass the message to the senders
async def send(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat
    user: telegram.User | None = update.effective_user
    message: telegram.Message | None = update.effective_message

    if chat is None or user is None or message is None:
        return

    message_text: str | None = message.text

    if message_text is None:
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session, user_id=user.id
        ).get()

    if not isinstance(db_user, libs.User):
        _ = await chat.send_message(
            (
                "You're not authorized. Please, type a /start command to "
                "initiate an authorization"
            )
        )
        return

    with compiled_session() as session:
        session.add(db_user)
        is_user_authorizing: bool = libs.DBUserManipulator(
            session, db_user=db_user
        ).get_authorizing_status()

    if is_user_authorizing:
        try:
            hex_token: libs.HexToken = libs.HexToken(message_text)
        except ValueError:
            _ = await chat.send_message(
                (
                    "The token contains not-compitable symbols. Please, check "
                    "your token and try again"
                )
            )
            return

        with compiled_session() as session:
            valid_token: libs.ValidToken | None = libs.DBValidTokenGetter(
                session, hex_token.get()
            ).get()

        if not isinstance(valid_token, libs.ValidToken):
            _ = await chat.send_message(
                "The token is not valid. Please, provide an another token"
            )
            return

        if hex_token.get() != valid_token.token:
            _ = await chat.send_message(
                "The token is not valid. Please, provide an another token"
            )
            return

        # On this step, the user is pass the challenges, so the user is
        # authorized
        with compiled_session() as session:
            session.add(db_user)
            db_user_manipulator: libs.DBUserManipulator = (
                libs.DBUserManipulator(session, db_user=db_user)
            )
            db_user_manipulator.set_token(hex_token.get())
            db_user_manipulator.set_authorizing_status(False)
            session.commit()

        _ = await chat.send_message("You're authorized")
    else:
        email_sender.send(message_text)
        _ = await chat.send_message("Message have been sent")


async def post_init(_) -> None:
    print("Started")


# Creating an app and adding handlers
app = (
    ApplicationBuilder()
    .token(
        TELEGRAM_TOKEN
    )  # pyright: ignore[reportUnknownMemberType]  # type: ignore
    .post_init(post_init)
    .build()
)

# TODO make a `cancel` command
start_command_handler = CommandHandler("start", start)
message_handler = MessageHandler(filters.TEXT, send)

app.add_handler(start_command_handler)
app.add_handler(message_handler)

if __name__ == "__main__":
    app.run_polling()

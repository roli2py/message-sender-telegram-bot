from __future__ import annotations

from os import environ
from smtplib import SMTP
from typing import TYPE_CHECKING
from uuid import uuid4

import telegram
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.selectable import Select
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


# TODO move the algorithm to an another place
# Handler that authorize a user


"""
# Before
async def start(...):
    chat = ...
    user = ...

    if (chat or user) == None:
        stop
    
    get supposed_db_user where db_user.user_id == user.id from db
    
    if supposed_db_user != User:
        stop
    
    db_user = supposed_db_user

    get is_authorizing from db_user

    if is_authorizing:
        stop
    
    get supposed_token from db_user

    if supposed_token is null:
        stop
    
    token = supposed_token

    get supposed_valid_token where valid_token.token == token from db

    if supposed_valid_token is null:
        stop

# After
async def start(...):
    chat = ...
    user = ...

    if (chat or user) == None:
        stop
"""


# TODO move the functinos to another places
def get_db_user_authorizing_status(db_user: libs.User) -> bool:
    with compiled_session() as session:
        session.add(db_user)
        is_user_authorizing: bool = db_user.is_authorizing

    return is_user_authorizing


def set_db_user_authorizing_status(
    db_user: libs.User, is_authorizing: bool
) -> None:
    with compiled_session() as session:
        session.add(db_user)
        db_user.is_authorizing = is_authorizing
        session.commit()


def get_db_user(user_id: int) -> libs.User | None:
    with compiled_session() as session:
        select_user_stmt: Select[tuple[libs.User]] = select(libs.User).where(
            libs.User.user_id == user_id
        )
        db_user_or_none: libs.User | None = session.execute(
            select_user_stmt
        ).scalar_one_or_none()

    return db_user_or_none


def create_db_user(user_id: int) -> None:
    with compiled_session() as session:
        new_db_user: libs.User = libs.User(
            id_=uuid4(),
            user_id=user_id,
            token=None,
            is_authorizing=True,
        )
        session.add(new_db_user)
        session.commit()


def get_token_of_db_user(db_user: libs.User) -> str | None:
    with compiled_session() as session:
        session.add(db_user)
        token_or_none: str | None = db_user.token

    return token_or_none


def set_token_of_db_user(db_user: libs.User, token: str | None) -> None:
    with compiled_session() as session:
        session.add(db_user)
        db_user.token = token
        session.commit()


def get_valid_token(token: str) -> libs.ValidToken | None:
    with compiled_session() as session:
        select_token_stmt: Select[tuple[libs.ValidToken]] = select(
            libs.ValidToken
        ).where(libs.ValidToken.token == token)
        valid_token_or_none: libs.ValidToken | None = session.execute(
            select_token_stmt
        ).scalar_one_or_none()

    return valid_token_or_none


async def start(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat
    user: telegram.User | None = update.effective_user

    if chat is None or user is None:
        return

    db_user: libs.User | None = get_db_user(user.id)

    if not isinstance(db_user, libs.User):
        create_db_user(user.id)
        _ = await chat.send_message("Enter the token")

        return

    is_user_authorizing: bool = get_db_user_authorizing_status(db_user)

    if is_user_authorizing:
        _ = await chat.send_message("Enter the token")
        return

    token_or_none: str | None = get_token_of_db_user(db_user)

    if not isinstance(token_or_none, str):
        set_db_user_authorizing_status(db_user, True)

        _ = await chat.send_message(
            "Your token is expired. Please, enter a new token"
        )
        return

    token: str = token_or_none

    valid_token_or_none: libs.ValidToken | None = get_valid_token(token)

    if not isinstance(valid_token_or_none, libs.ValidToken):
        set_token_of_db_user(db_user, None)
        set_db_user_authorizing_status(db_user, True)

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

    db_user: libs.User | None = get_db_user(user.id)

    if not isinstance(db_user, libs.User):
        _ = await chat.send_message(
            (
                "You're not authorized. Please, type a /start command to "
                "initiate an authorization"
            )
        )
        return

    is_user_authorizing: bool = get_db_user_authorizing_status(db_user)

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

        valid_token_or_none: libs.ValidToken | None = get_valid_token(
            hex_token.get()
        )

        if not isinstance(valid_token_or_none, libs.ValidToken):
            _ = await chat.send_message(
                "The token is not valid. Please, provide an another token"
            )
            return

        valid_token: libs.ValidToken = valid_token_or_none

        if hex_token.get() != valid_token.token:
            _ = await chat.send_message(
                "The token is not valid. Please, provide an another token"
            )
            return

        # On this step, the user is pass the challenges, so the user is
        # authorized
        set_token_of_db_user(db_user, hex_token.get())
        set_db_user_authorizing_status(db_user, False)

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

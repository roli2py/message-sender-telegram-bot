from __future__ import annotations

import re
from os import environ
from smtplib import SMTP
from typing import TYPE_CHECKING

import telegram
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.constants import ChatType, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
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

smtp: SMTP = libs.GmailSMTPCreator(
    GMAIL_SMTP_LOGIN,
    GMAIL_SMTP_PASSWORD,
).create()
email_sender: libs.EmailSender = libs.EmailSender(
    smtp,
    EMAIL_FROM_ADDR,
    EMAIL_TO_ADDR,
)


# Handler that starts an authorization process
async def start(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat

    if chat is None:
        return

    user: telegram.User | None = update.effective_user

    if user is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session,
            user_id=user.id,
        ).get()

    # If a DB user is not exist, starting an authorization process
    if not isinstance(db_user, libs.User):
        with compiled_session() as session:
            # A creating of a DB user starts an authorization process
            new_db_user: libs.User = libs.DBUserManipulator(
                session,
                user_id=user.id,
            ).create()
            session.add(new_db_user)
            session.commit()

        _ = await chat.send_message("Enter the token")

        return

    with compiled_session() as session:
        session.add(db_user)
        is_user_authorizing: bool = libs.DBUserManipulator(
            session,
            db_user=db_user,
        ).get_authorizing_status()

    if is_user_authorizing:
        _ = await chat.send_message("Enter the token")
        return

    with compiled_session() as session:
        session.add(db_user)
        valid_token: libs.ValidToken | None = libs.DBUserManipulator(
            session,
            db_user=db_user,
        ).get_valid_token()

    # If a DB user is authorized and a DB valid token is not exist, then
    # the token is expired and the user must enter a new token
    if not isinstance(valid_token, libs.ValidToken):
        with compiled_session() as session:
            session.add(db_user)
            libs.DBUserManipulator(
                session,
                db_user=db_user,
            ).set_authorizing_status(True)
            session.commit()

        _ = await chat.send_message(
            "Your token is expired. Please, enter a new token"
        )
        return

    # If other cases is not invoked, then the user is authorized
    _ = await chat.send_message("You're already authorized")


async def confirm_send(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat

    if chat is None:
        return

    user: telegram.User | None = update.effective_user

    if user is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    message: telegram.Message | None = update.effective_message

    if message is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    message_text: str | None = message.text

    if message_text is None:
        _ = await chat.send_message(
            "Your message doesn't have a text. Send a message with a text"
        )
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session,
            user_id=user.id,
        ).get()

    # If a DB user is not exists, then he's not authozired
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
            session,
            db_user=db_user,
        ).get_authorizing_status()

    if is_user_authorizing:
        # Assuming, that a user invoked a `start` command and this
        # message contains an authorization token
        try:
            hex_token: libs.HexToken = libs.HexToken(message_text)
        # When a hex token is wrong, the constructor will throw a
        # `ValueError` exception
        except ValueError:
            _ = await chat.send_message(
                (
                    "The token contains not-compitable symbols. Please, check "
                    "your token and try again"
                )
            )
            return

        with compiled_session() as session:
            session.add(db_user)
            valid_token: libs.ValidToken | None = libs.DBValidTokenManipulator(
                session,
                hex_token.get(),
            ).get()

        # If a DB valid token with a user-provided token is not exist,
        # then the token is expired or invalid
        if not isinstance(valid_token, libs.ValidToken):
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
            db_user_manipulator.set_valid_token(valid_token)
            db_user_manipulator.set_authorizing_status(False)
            session.commit()

        _ = await chat.send_message("You're authorized")
    else:
        yes_button: telegram.InlineKeyboardButton = (
            telegram.InlineKeyboardButton(
                "Yes",
                callback_data=f"message_confirmation,true,{message_text}",
            )
        )
        no_button: telegram.InlineKeyboardButton = (
            telegram.InlineKeyboardButton(
                "No",
                callback_data="message_confirmation,false",
            )
        )
        reply_markup: telegram.InlineKeyboardMarkup = (
            telegram.InlineKeyboardMarkup([[yes_button, no_button]])
        )
        _ = await chat.send_message(
            "Send a message?",
            reply_markup=reply_markup,
        )


# Handler that pass the message to the senders
async def send(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat

    if chat is None:
        return

    user: telegram.User | None = update.effective_user

    if user is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    message: telegram.Message | None = update.effective_message

    if message is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session, user_id=user.id
        ).get()

    # If a DB user is not exists, then he's not authozired
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
        _ = await chat.send_message("Send a token to authorize")

    callback_query: telegram.CallbackQuery | None = update.callback_query

    if callback_query is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    callback_query_data: str | None = callback_query.data

    if callback_query_data is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    # Callback data of this handler always has the text on the index 2
    # after the split
    message_text: str = callback_query_data.split(",")[2]

    email_sender.set_sender_name(user.name)
    email_sender.send(message_text)
    _ = await chat.send_message("Message have been sent")
    _ = await callback_query.answer()


async def cancel(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat

    if chat is None:
        return

    user: telegram.User | None = update.effective_user

    if user is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    with compiled_session() as session:
        db_user: libs.User | None = libs.DBUserManipulator(
            session, user_id=user.id
        ).get()

    if isinstance(db_user, libs.User):
        with compiled_session() as session:
            session.add(db_user)
            is_user_authorizing: bool = libs.DBUserManipulator(
                session, db_user=db_user
            ).get_authorizing_status()

        if is_user_authorizing:
            with compiled_session() as session:
                session.add(db_user)
                session.delete(db_user)
                session.commit()

            _ = await chat.send_message("An authorizing have been canceled")

            return

    callback_query: telegram.CallbackQuery | None = update.callback_query

    if callback_query is not None:
        data: str | None = callback_query.data

        if data is None:
            _ = await chat.send_message("An unknown error is occured")
            return

        _ = await chat.send_message("The message send have been canceled")
        _ = await callback_query.answer()
        return

    _ = await chat.send_message("Nothing to cancel")


async def notify_about_unknown_command(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat

    if chat is None:
        return

    _ = await chat.send_message("An unknown command")


async def show_admin_panel(
    update: telegram.Update, ctx: ContextTypes.DEFAULT_TYPE
) -> None:
    chat: telegram.Chat | None = update.effective_chat
    user: telegram.User | None = update.effective_user

    if chat is None:
        return

    if user is None:
        _ = await chat.send_message("You're not owner of the bot")
        return

    with compiled_session() as session:
        db_user_manipulator: libs.DBUserManipulator = libs.DBUserManipulator(
            session, user_id=user.id
        )
        _ = db_user_manipulator.get()
        is_user_owner: bool = libs.UserOwnershipProver(
            db_user_manipulator
        ).prove()

    if not is_user_owner:
        await notify_about_unknown_command(update, ctx)
        return

    reply_markup: telegram.InlineKeyboardMarkup = (
        telegram.InlineKeyboardMarkup(
            (
                (
                    telegram.InlineKeyboardButton(
                        "Generate a token", callback_data="generate_token"
                    ),
                ),
            )
        )
    )
    _ = await chat.send_message(
        "What do you want to do?", reply_markup=reply_markup
    )


async def generate_token(
    update: telegram.Update,
    ctx: ContextTypes.DEFAULT_TYPE,  # pyright: ignore[reportUnusedParameter]  # type: ignore
) -> None:
    chat: telegram.Chat | None = update.effective_chat
    user: telegram.User | None = update.effective_user
    callback_query: telegram.CallbackQuery | None = update.callback_query

    if chat is None:
        return

    if user is None or callback_query is None:
        _ = await chat.send_message("An unknown error is occured")
        return

    with compiled_session() as session:
        db_user_manipulator: libs.DBUserManipulator = libs.DBUserManipulator(
            session, user_id=user.id
        )
        _ = db_user_manipulator.get()
        is_user_owner: bool = libs.UserOwnershipProver(
            db_user_manipulator
        ).prove()

    if not is_user_owner:
        _ = await chat.send_message("You're not owner of the bot")
        return

    hex_token: libs.Token = libs.HexTokenCreator().create()

    with compiled_session() as session:
        new_valid_token: libs.ValidToken = libs.DBValidTokenManipulator(
            session, hex_token.get()
        ).create()
        session.add(new_valid_token)
        session.commit()

    if chat.type != ChatType.PRIVATE:
        _ = await chat.send_message("Sent a new token to DM")

    _ = await user.send_message(
        f"Here's a new token:\n`{hex_token.get()}`",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    _ = await callback_query.answer()


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

start_command_handler = CommandHandler("start", start)
admin_command_handler = CommandHandler("admin", show_admin_panel)
cancel_command_handler = CommandHandler("cancel", cancel)
unknown_command_handler = MessageHandler(
    filters.COMMAND, notify_about_unknown_command
)
token_generation_request_handler = CallbackQueryHandler(
    generate_token, re.compile(r"^generate_token$")
)
message_send_handler = CallbackQueryHandler(
    send, re.compile(r"^message_confirmation,true")
)
message_cancel_handler = CallbackQueryHandler(
    cancel, re.compile(r"^message_confirmation,false$")
)
message_handler = MessageHandler(filters.TEXT, confirm_send)

app.add_handler(start_command_handler)
app.add_handler(admin_command_handler)
app.add_handler(cancel_command_handler)
app.add_handler(unknown_command_handler)
app.add_handler(token_generation_request_handler)
app.add_handler(message_send_handler)
app.add_handler(message_cancel_handler)
app.add_handler(message_handler)

if __name__ == "__main__":
    app.run_polling()

from __future__ import annotations

from datetime import datetime
from secrets import token_hex
from typing import TYPE_CHECKING

import telegram
from telegram.constants import ChatType, ParseMode

from . import consts, fstrings
from .consts import ButtonTexts
from .rdb import (
    DBMessageManipulator,
    DBUserManipulator,
    DBValidTokenManipulator,
    database_tables,
)

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy.orm import Session, sessionmaker
    from telegram.ext import ContextTypes

    from .helpers import Helpers
    from .types import Token


class Handlers:
    def __init__(
        self: Self,
        compiled_session: sessionmaker[Session],
        helpers: Helpers,
    ) -> None:
        self.__compiled_session: sessionmaker[Session] = compiled_session
        self.__helpers: Helpers = helpers

    # Handler that starts an authorization process
    async def start(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session,
                user_id=user.id,
            ).get()

        # If a DB user is not exist, starting an authorization process
        if db_user is None:
            with self.__compiled_session() as session:
                # A creating of a DB user starts an authorization process
                new_db_user: database_tables.User = DBUserManipulator(
                    session,
                    user_id=user.id,
                ).create()

                session.add(new_db_user)

                session.commit()

            await chat.send_message(consts.Answers.ENTER_TOKEN)

            return None

        with self.__compiled_session() as session:
            session.add(db_user)

            is_user_authorizing: bool = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_authorizing_status()

        if is_user_authorizing:
            await chat.send_message(consts.Answers.ENTER_TOKEN)

            return None

        with self.__compiled_session() as session:
            session.add(db_user)

            valid_token: database_tables.ValidToken | None = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_valid_token()

        # If a DB user is authorized and a DB valid token is not exist, then
        # the token is expired and the user must enter a new token
        if valid_token is None:
            with self.__compiled_session() as session:
                session.add(db_user)

                DBUserManipulator(
                    session,
                    db_user=db_user,
                ).set_authorizing_status(True)

                session.commit()

            await chat.send_message(consts.Answers.TOKEN_IS_EXPIRED)

            return None

        # If other cases is not invoked, then the user is authorized
        await chat.send_message(consts.Answers.TOKEN_IS_EXPIRED)

        return None

    async def handle_message(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user
        message: telegram.Message | None = update.effective_message

        if user is None or message is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        message_text: str | None = message.text

        if message_text is None:
            await chat.send_message(consts.Answers.MESSAGE_DOESNT_HAVE_TEXT)

            return None

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session,
                user_id=user.id,
            ).get()

        # If a DB user is not exists, then the user is not authorized
        if db_user is None:
            await chat.send_message(consts.Answers.NOT_AUTHORIZED)

            return None

        with self.__compiled_session() as session:
            session.add(db_user)

            is_user_authorizing: bool = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_authorizing_status()

        if is_user_authorizing:
            await self.__helpers.authorize(chat, message_text, db_user)

            return None

        (
            is_cooldown_pass,
            remaining_time,
        ) = await self.__helpers.check_cooldown(db_user)

        if not is_cooldown_pass:
            await chat.send_message(
                fstrings.Answers.send_message_after_seconds.format(
                    seconds=remaining_time.seconds
                )
            )

            return None

        with self.__compiled_session() as session:
            session.add(db_user)

            db_message = DBMessageManipulator(
                session,
                message.id,
                sender=db_user,
                text=message_text,
            ).create()
            session.add(db_message)

            session.commit()

        await self.__helpers.show_message_confirmation_panel(chat, message.id)

        return None

    # Handler that pass the message to the senders
    async def send(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user
        message: telegram.Message | None = update.effective_message

        if user is None or message is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session, user_id=user.id
            ).get()

        # If a DB user is not exists, then the user is not authorized
        if db_user is None:
            await chat.send_message(consts.Answers.NOT_AUTHORIZED)

            return None

        with self.__compiled_session() as session:
            session.add(db_user)

            is_user_authorizing: bool = DBUserManipulator(
                session, db_user=db_user
            ).get_authorizing_status()

        if is_user_authorizing:
            await chat.send_message(consts.Answers.SEND_TOKEN)

        (
            is_cooldown_pass,
            remaining_time,
        ) = await self.__helpers.check_cooldown(db_user)

        if not is_cooldown_pass:
            await chat.send_message(
                fstrings.Answers.send_message_after_seconds.format(
                    seconds=remaining_time.seconds
                )
            )

            return None

        callback_query: telegram.CallbackQuery | None = update.callback_query

        if callback_query is None:
            await chat.send_message(consts.Answers.SEND_TOKEN)

            return None

        callback_data: str | None = callback_query.data

        if callback_data is None:
            await chat.send_message(consts.Answers.SEND_TOKEN)

            return None

        # A message ID will be always a third item after the split
        assigned_message_id = int(callback_data.split(",")[2])

        with self.__compiled_session() as session:
            db_message: database_tables.Message | None = DBMessageManipulator(
                session,
                assigned_message_id,
            ).get()

        if db_message is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        if db_message.sender_id != db_user.id_:
            await chat.send_message(consts.Answers.NOT_SENDER_OF_MESSAGE)

            return None

        if db_message.is_sent:
            await message.edit_text(consts.Answers.MESSAGE_ALREADY_WAS_SENT)
            await callback_query.answer()

            return None

        self.__helpers.send_email(user.name, db_message.text)

        with self.__compiled_session() as session:
            session.add(db_message)
            session.add(db_user)

            db_message.is_sent = True
            db_user.last_send_date = datetime.now()

            session.commit()

        await message.edit_text(consts.Answers.MESSAGE_SENT)
        await callback_query.answer()

        return None

    async def cancel(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session, user_id=user.id
            ).get()

        # If the user exists, then the bot must check, that the user is
        # authorizing or not and, if the user is authorizing, cancel the
        # authorization process
        if db_user is not None:
            with self.__compiled_session() as session:
                session.add(db_user)

                is_user_authorizing: bool = DBUserManipulator(
                    session, db_user=db_user
                ).get_authorizing_status()

            # If the user is authorizing, then the user want to cancel
            # an authorization process. Therefore, the bot will delete
            # the DB user
            if is_user_authorizing:
                with self.__compiled_session() as session:
                    session.delete(db_user)

                    session.commit()

                await chat.send_message(consts.Answers.AUTHORIZATION_CANCELED)

                return None

        callback_query: telegram.CallbackQuery | None = update.callback_query

        # If the callback query exists, then the message send was rejected
        if callback_query is not None:
            message: telegram.Message | None = update.effective_message
            callback_data: str | None = callback_query.data

            if message is None or callback_data is None:
                await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

                return None

            # A message ID will be always a third item after the split
            assigned_message_id = int(callback_data.split(",")[2])

            with self.__compiled_session() as session:
                db_message: database_tables.Message | None = (
                    DBMessageManipulator(
                        session,
                        assigned_message_id,
                    ).get()
                )

            if db_message is None:
                await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

                return None

            if db_user is None or db_message.sender_id != db_user.id_:
                await chat.send_message(consts.Answers.NOT_SENDER_OF_MESSAGE)

                return None

            # Because a bug can occur and the message can be sent again,
            # the bot checks, that the message was sent or not
            if db_message.is_sent:
                await message.edit_text(
                    consts.Answers.MESSAGE_ALREADY_WAS_SENT,
                )
                await callback_query.answer()

                return None

            # Rejecting the message by deleting it from DB
            with self.__compiled_session() as session:
                session.delete(db_message)

                session.commit()

            await message.edit_text(consts.Answers.MESSAGE_SEND_CANCELED)
            await callback_query.answer()

            return None

        await chat.send_message(consts.Answers.NOTHING_TO_CANCEL)

        return None

    async def notify_about_unknown_command(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        await chat.send_message(consts.Answers.UNKNOWN_COMMAND)

        return None

    # TODO realize a "Delete a token" button
    # TODO realize a "List tokens" button
    async def show_admin_panel(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(consts.Answers.NOT_OWNER_OF_BOT)

            return None

        is_user_owner = await self.__helpers.is_user_owner(user.id)

        if not is_user_owner:
            await self.notify_about_unknown_command(update, ctx)

            return None

        reply_markup: telegram.InlineKeyboardMarkup = (
            telegram.InlineKeyboardMarkup(
                (
                    (
                        telegram.InlineKeyboardButton(
                            ButtonTexts.GENERATE_TOKEN,
                            callback_data="generate_token",
                        ),
                    ),
                )
            )
        )
        await chat.send_message(
            consts.Answers.WHAT_DO_YOU_WANT,
            reply_markup=reply_markup,
        )

        return None

    async def generate_token(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return None

        user: telegram.User | None = update.effective_user
        callback_query: telegram.CallbackQuery | None = update.callback_query

        if user is None or callback_query is None:
            await chat.send_message(consts.Answers.UNKNOWN_ERROR_OCCURS)

            return None

        is_user_owner = await self.__helpers.is_user_owner(user.id)

        if not is_user_owner:
            await chat.send_message(consts.Answers.NOT_OWNER_OF_BOT)

            return None

        hex_token: Token = Token(token_hex())

        with self.__compiled_session() as session:
            new_valid_token: database_tables.ValidToken = (
                DBValidTokenManipulator(session, hex_token).create()
            )

            session.add(new_valid_token)

            session.commit()

        if chat.type != ChatType.PRIVATE:
            await chat.send_message(consts.Answers.SENT_TOKEN_TO_DM)

        await user.send_message(
            fstrings.Answers.new_token.format(token=hex_token),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await callback_query.answer()

        return None

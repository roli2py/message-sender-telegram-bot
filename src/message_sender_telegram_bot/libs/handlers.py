from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import telegram
from telegram.constants import ChatType, ParseMode

from . import database_tables
from .consts import Answers, ButtonTexts
from .db_message_manipulator import DBMessageManipulator
from .db_user_manipulators import DBUserManipulator
from .db_valid_token_manipulator import DBValidTokenManipulator
from .ownership_provers import UserOwnershipProver
from .token_creators import HexTokenCreator
from .tokens import Token

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy.orm import Session, sessionmaker
    from telegram.ext import ContextTypes

    from .helpers import Helpers


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
            return

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session,
                user_id=user.id,
            ).get()

        # If a DB user is not exist, starting an authorization process
        if not isinstance(db_user, database_tables.User):
            with self.__compiled_session() as session:
                # A creating of a DB user starts an authorization process
                new_db_user: database_tables.User = DBUserManipulator(
                    session,
                    user_id=user.id,
                ).create()
                session.add(new_db_user)
                session.commit()

            await chat.send_message(Answers.ENTER_TOKEN)

            return

        with self.__compiled_session() as session:
            session.add(db_user)
            is_user_authorizing: bool = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_authorizing_status()

        if is_user_authorizing:
            await chat.send_message(Answers.ENTER_TOKEN)
            return

        with self.__compiled_session() as session:
            session.add(db_user)
            valid_token: database_tables.ValidToken | None = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_valid_token()

        # If a DB user is authorized and a DB valid token is not exist, then
        # the token is expired and the user must enter a new token
        if not isinstance(valid_token, database_tables.ValidToken):
            with self.__compiled_session() as session:
                session.add(db_user)
                DBUserManipulator(
                    session,
                    db_user=db_user,
                ).set_authorizing_status(True)
                session.commit()

            await chat.send_message(Answers.TOKEN_IS_EXPIRED)
            return

        # If other cases is not invoked, then the user is authorized
        await chat.send_message(Answers.TOKEN_IS_EXPIRED)

    async def handle_message(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        message: telegram.Message | None = update.effective_message

        if message is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        message_text: str | None = message.text

        if message_text is None:
            await chat.send_message(Answers.MESSAGE_DOESNT_HAVE_TEXT)
            return

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session,
                user_id=user.id,
            ).get()

        # If a DB user is not exists, then he's not authorized
        if not isinstance(db_user, database_tables.User):
            await chat.send_message(Answers.NOT_AUTHORIZED)
            return

        with self.__compiled_session() as session:
            session.add(db_user)
            is_user_authorizing: bool = DBUserManipulator(
                session,
                db_user=db_user,
            ).get_authorizing_status()

        if is_user_authorizing:
            await self.__helpers.authorize(chat, message_text, db_user)
            return
        else:
            (
                is_cooldown_pass,
                remaining_cooldown,
            ) = await self.__helpers.check_cooldown(db_user)

            if not is_cooldown_pass:
                await chat.send_message(
                    (
                        # TODO move to consts (?)
                        f"Send the message again after "
                        f"{remaining_cooldown.seconds} seconds"
                    )
                )
                return

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

            await self.__helpers.show_message_confirmation_panel(
                chat, message.id
            )

            return

    # Handler that pass the message to the senders
    async def send(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        message: telegram.Message | None = update.effective_message

        if message is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session, user_id=user.id
            ).get()

        # If a DB user is not exists, then he's not authozired
        if not isinstance(db_user, database_tables.User):
            await chat.send_message(Answers.NOT_AUTHORIZED)
            return

        with self.__compiled_session() as session:
            session.add(db_user)
            is_user_authorizing: bool = DBUserManipulator(
                session, db_user=db_user
            ).get_authorizing_status()

        if is_user_authorizing:
            await chat.send_message(Answers.SEND_TOKEN)

        (
            is_cooldown_pass,
            remaining_cooldown,
        ) = await self.__helpers.check_cooldown(db_user)

        if not is_cooldown_pass:
            await chat.send_message(
                (
                    # TODO move to consts (?)
                    f"Send the message again after {remaining_cooldown.seconds} "
                    f"seconds"
                )
            )
            return

        callback_query: telegram.CallbackQuery | None = update.callback_query

        if callback_query is None:
            await chat.send_message(Answers.SEND_TOKEN)
            return

        callback_data: str | None = callback_query.data

        if callback_data is None:
            await chat.send_message(Answers.SEND_TOKEN)
            return

        # A message ID will be always a third item after the split
        assigned_message_id = int(callback_data.split(",")[2])

        with self.__compiled_session() as session:
            db_message: database_tables.Message | None = DBMessageManipulator(
                session,
                assigned_message_id,
            ).get()

        if db_message is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        if db_message.is_sent:
            await message.edit_text(Answers.MESSAGE_ALREADY_WAS_SENT)
            await callback_query.answer()
            return

        self.__helpers.send_email(user.name, db_message.text)

        with self.__compiled_session() as session:
            session.add(db_message)
            session.add(db_user)

            db_message.is_sent = True
            db_user.last_send_date = datetime.now()

            session.commit()

        await message.edit_text(Answers.MESSAGE_SENT)
        await callback_query.answer()

    async def cancel(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return

        user: telegram.User | None = update.effective_user

        if user is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        with self.__compiled_session() as session:
            db_user: database_tables.User | None = DBUserManipulator(
                session, user_id=user.id
            ).get()

        if isinstance(db_user, database_tables.User):
            with self.__compiled_session() as session:
                session.add(db_user)
                is_user_authorizing: bool = DBUserManipulator(
                    session, db_user=db_user
                ).get_authorizing_status()

            if is_user_authorizing:
                with self.__compiled_session() as session:
                    session.add(db_user)
                    session.delete(db_user)
                    session.commit()

                await chat.send_message(Answers.AUTHORIZATION_CANCELED)

                return

        callback_query: telegram.CallbackQuery | None = update.callback_query

        if callback_query is not None:
            message: telegram.Message | None = update.effective_message

            if message is None:
                await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
                return

            callback_data: str | None = callback_query.data

            if callback_data is None:
                await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
                return

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
                await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
                return

            if db_message.is_sent:
                await message.edit_text(Answers.MESSAGE_ALREADY_WAS_SENT)
                await callback_query.answer()
                return

            with self.__compiled_session() as session:
                session.delete(db_message)
                session.commit()

            await message.edit_text(Answers.MESSAGE_SEND_CANCELED)
            await callback_query.answer()

            return

        await chat.send_message(Answers.NOTHING_TO_CANCEL)

    async def notify_about_unknown_command(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat

        if chat is None:
            return

        await chat.send_message(Answers.UNKNOWN_COMMAND)

    # TODO realize a "Delete a token" button
    # TODO realize a "List tokens" button
    async def show_admin_panel(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat
        user: telegram.User | None = update.effective_user

        if chat is None:
            return

        if user is None:
            await chat.send_message(Answers.YOURE_NOT_OWNER)
            return

        with self.__compiled_session() as session:
            db_user_manipulator: DBUserManipulator = DBUserManipulator(
                session, user_id=user.id
            )
            db_user_manipulator.get()
            is_user_owner: bool = UserOwnershipProver(
                db_user_manipulator
            ).prove()

        if not is_user_owner:
            await self.notify_about_unknown_command(update, ctx)
            return

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
            Answers.WHAT_DO_YOU_WANT,
            reply_markup=reply_markup,
        )

    async def generate_token(
        self: Self,
        update: telegram.Update,
        ctx: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        chat: telegram.Chat | None = update.effective_chat
        user: telegram.User | None = update.effective_user
        callback_query: telegram.CallbackQuery | None = update.callback_query

        if chat is None:
            return

        if user is None or callback_query is None:
            await chat.send_message(Answers.UNKNOWN_ERROR_OCCURED)
            return

        with self.__compiled_session() as session:
            db_user_manipulator: DBUserManipulator = DBUserManipulator(
                session, user_id=user.id
            )
            db_user_manipulator.get()
            is_user_owner: bool = UserOwnershipProver(
                db_user_manipulator
            ).prove()

        if not is_user_owner:
            await chat.send_message(Answers.YOURE_NOT_OWNER)
            return

        hex_token: Token = HexTokenCreator().create()

        with self.__compiled_session() as session:
            new_valid_token: database_tables.ValidToken = (
                DBValidTokenManipulator(session, hex_token.get()).create()
            )
            session.add(new_valid_token)
            session.commit()

        if chat.type != ChatType.PRIVATE:
            await chat.send_message(Answers.SENT_TOKEN_TO_DM)

        await user.send_message(
            # TODO move to consts (?)
            f"Here's a new token:\n`{hex_token.get()}`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await callback_query.answer()

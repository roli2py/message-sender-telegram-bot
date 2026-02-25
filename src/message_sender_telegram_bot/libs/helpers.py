from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import telegram

from . import database_tables
from .consts import Answers, ButtonTexts
from .cooldown_checkers import MessageSendCooldownChecker
from .db_user_manipulators import DBUserManipulator
from .db_valid_token_manipulator import DBValidTokenManipulator
from .senders.email_sender import EmailSender
from .smtp_creators.gmail_smtp_creator import GmailSMTPCreator
from .tokens import HexToken

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy.orm import Session, sessionmaker

    from .types import CooldownCheckResult


class Helpers:
    def __init__(
        self: Self,
        gmail_smtp_login: str,
        gmail_smtp_password: str,
        email_from_addr: str,
        email_to_addr: str,
        compiled_session: sessionmaker[Session],
    ) -> None:
        self.__gmail_smtp_login: str = gmail_smtp_login
        self.__gmail_smtp_password: str = gmail_smtp_password
        self.__email_from_addr: str = email_from_addr
        self.__email_to_addr: str = email_to_addr
        self.__compiled_session: sessionmaker[Session] = compiled_session

    async def authorize(
        self: Self,
        chat: telegram.Chat,
        message_text: str,
        db_user: database_tables.User,
    ) -> None:
        # Assuming, that a user invoked a `start` command and this
        # message contains an authorization token
        try:
            hex_token: HexToken = HexToken(message_text)
        # When a hex token is wrong, the constructor will throw a
        # `ValueError` exception
        except ValueError:
            await chat.send_message(Answers.NOT_COMPITABLE_SYMBOLS_IN_TOKEN)
            return

        with self.__compiled_session() as session:
            session.add(db_user)
            valid_token: database_tables.ValidToken | None = (
                DBValidTokenManipulator(
                    session,
                    hex_token.get(),
                ).get()
            )

        # If a DB valid token with a user-provided token is not exist,
        # then the token is expired or invalid
        if not isinstance(valid_token, database_tables.ValidToken):
            await chat.send_message(Answers.TOKEN_IS_NOT_VALID)
            return

        # On this step, the user is pass the challenges, so the user is
        # authorized
        with self.__compiled_session() as session:
            session.add(db_user)
            db_user_manipulator: DBUserManipulator = DBUserManipulator(
                session, db_user=db_user
            )
            db_user_manipulator.set_valid_token(valid_token)
            db_user_manipulator.set_authorizing_status(False)
            session.commit()

        await chat.send_message(Answers.AUTHORIZED)

    def send_email(self: Self, name: str, text: str) -> None:
        with GmailSMTPCreator(
            self.__gmail_smtp_login,
            self.__gmail_smtp_password,
        ) as smtp:
            email_sender: EmailSender = EmailSender(
                smtp,
                self.__email_from_addr,
                self.__email_to_addr,
                sender_name=name,
            )
            email_sender.send(text)

    async def show_message_confirmation_panel(
        self: Self,
        chat: telegram.Chat,
        message_id: int,
    ) -> None:
        yes_button: telegram.InlineKeyboardButton = (
            telegram.InlineKeyboardButton(
                ButtonTexts.YES,
                callback_data=f"message_confirmation,true,{message_id}",
            )
        )

        no_button: telegram.InlineKeyboardButton = (
            telegram.InlineKeyboardButton(
                ButtonTexts.NO,
                callback_data=f"message_confirmation,false,{message_id}",
            )
        )

        reply_markup: telegram.InlineKeyboardMarkup = (
            telegram.InlineKeyboardMarkup([[yes_button, no_button]])
        )
        await chat.send_message(
            Answers.SEND_MESSAGE_QUESTION,
            reply_markup=reply_markup,
        )

    async def check_cooldown(
        self: Self,
        db_user: database_tables.User,
    ) -> CooldownCheckResult:
        with self.__compiled_session() as session:
            session.add(db_user)
            last_send_date: datetime | None = db_user.last_send_date

        if last_send_date is None:
            return CooldownCheckResult(True, timedelta())

        cooldown: timedelta = timedelta(seconds=30)

        is_cooldown_pass: bool = MessageSendCooldownChecker(
            last_send_date,
            cooldown=cooldown,
        ).is_pass()

        if is_cooldown_pass:
            return CooldownCheckResult(True, timedelta())

        diff_between_dates: timedelta = datetime.now() - last_send_date
        remaining_cooldown: timedelta = cooldown - diff_between_dates

        return CooldownCheckResult(False, remaining_cooldown)

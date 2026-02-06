from smtplib import SMTP
from typing import Self, override

from pytest import fixture, raises

from message_sender_telegram_bot.libs import SMTPCreator


@fixture
def smtp_creator_wrapper() -> SMTPCreator:
    class SMTPCreatorWrapper(SMTPCreator):
        @override
        def create(self: Self) -> SMTP:
            return super().create()

    return SMTPCreatorWrapper()


def test_disallow_of_a_creation_of_a_smtp_creator_interface_instance() -> None:
    with raises(TypeError):
        _ = SMTPCreator()


def test_disallow_of_a_direct_using_of_a_create_method(
    smtp_creator_wrapper: SMTPCreator,
) -> None:
    with raises(NotImplementedError):
        _ = smtp_creator_wrapper.create()

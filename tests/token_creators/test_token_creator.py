from typing import Self, override

from pytest import fixture, raises

from message_sender_telegram_bot.libs import Token, TokenCreator


@fixture
def token_creator_wrapper() -> TokenCreator:
    class TokenCreatorWrapper(TokenCreator):
        @override
        def create(self: Self) -> Token:
            return super().create()

    return TokenCreatorWrapper()


def test_disallow_of_a_creation_of_a_token_creator_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = TokenCreator()


def test_disallow_of_a_direct_using_of_a_create_method(
    token_creator_wrapper: TokenCreator,
) -> None:
    with raises(NotImplementedError):
        _ = token_creator_wrapper.create()

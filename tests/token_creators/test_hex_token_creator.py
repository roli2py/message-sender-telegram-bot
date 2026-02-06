from pytest import fixture

from message_sender_telegram_bot.libs import HexToken, HexTokenCreator, Token


@fixture
def hex_token_creator() -> HexTokenCreator:
    return HexTokenCreator()


def test_a_creation_of_a_hex_token(hex_token_creator: HexTokenCreator) -> None:
    hex_token: Token = hex_token_creator.create()

    assert isinstance(hex_token, HexToken)

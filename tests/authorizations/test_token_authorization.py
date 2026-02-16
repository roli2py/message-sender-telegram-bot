from unittest.mock import patch

from pytest import fixture

from message_sender_telegram_bot.libs import HexToken, TokenAuthorization


@fixture
@patch("message_sender_telegram_bot.libs.HexToken", get="0123456789abcdef")
def valid_token(hex_token_mock: HexToken) -> HexToken:
    return hex_token_mock


@fixture
@patch("message_sender_telegram_bot.libs.HexToken", get="abcdef0123456789")
def invalid_token(hex_token_mock: HexToken) -> HexToken:
    return hex_token_mock


@fixture
def valid_tokens(valid_token: HexToken) -> set[HexToken]:
    return {valid_token}


@fixture
def token_authorization(
    valid_tokens: set[HexToken], valid_token: HexToken
) -> TokenAuthorization:
    return TokenAuthorization(valid_tokens, valid_token)


@fixture
def token_authorization_with_invalid_token(
    valid_tokens: set[HexToken], invalid_token: HexToken
) -> TokenAuthorization:
    return TokenAuthorization(valid_tokens, invalid_token)


def test_authorization(token_authorization: TokenAuthorization) -> None:
    is_authorized: bool = token_authorization.authorize()

    assert isinstance(is_authorized, bool)
    assert is_authorized


def test_authorization_with_invalid_token(
    token_authorization_with_invalid_token: TokenAuthorization,
) -> None:
    is_authorized: bool = token_authorization_with_invalid_token.authorize()

    assert isinstance(is_authorized, bool)
    assert not is_authorized

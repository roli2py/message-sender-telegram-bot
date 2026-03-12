from pytest import fixture

from message_sender_telegram_bot.libs import TokenAuthorization
from message_sender_telegram_bot.libs.types import Token


@fixture
def valid_token() -> Token:
    return Token("0123456789abcdef")


@fixture
def invalid_token() -> Token:
    return Token("abcdef0123456789")


@fixture
def valid_tokens(valid_token: Token) -> set[Token]:
    return {valid_token}


@fixture
def token_authorization(
    valid_tokens: set[Token],
    valid_token: Token,
) -> TokenAuthorization:
    return TokenAuthorization(valid_tokens, valid_token)


@fixture
def token_authorization_with_invalid_token(
    valid_tokens: set[Token],
    invalid_token: Token,
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

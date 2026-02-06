from pytest import fixture, raises

from message_sender_telegram_bot.libs import HexToken


@fixture
def raw_lowercase_hex_token() -> str:
    return "123456789abcdef"


@fixture
def raw_uppercase_hex_token() -> str:
    return "123456789ABCDEF"


@fixture
def raw_mixedcase_hex_token() -> str:
    return "123456789aBcDEf"


@fixture
def raw_wrong_token() -> str:
    return "hLLOWorlHllowORl"


def test_an_accept_of_a_lowercase_hex_token(
    raw_lowercase_hex_token: str,
) -> None:
    _ = HexToken(raw_lowercase_hex_token)


def test_an_accept_of_a_uppercase_hex_token(
    raw_uppercase_hex_token: str,
) -> None:
    _ = HexToken(raw_uppercase_hex_token)


def test_an_accept_of_a_mixedcase_hex_token(
    raw_mixedcase_hex_token: str,
) -> None:
    _ = HexToken(raw_mixedcase_hex_token)


def test_a_reject_of_a_wrong_token(raw_wrong_token: str) -> None:
    with raises(ValueError):
        _ = HexToken(raw_wrong_token)


@fixture
def hex_token(raw_lowercase_hex_token: str) -> HexToken:
    return HexToken(raw_lowercase_hex_token)


def test_a_get_of_a_raw_hex_token(
    hex_token: HexToken,
    # A raw token that supplied to the `hex_token` fixture
    raw_lowercase_hex_token: str,
) -> None:
    raw_hex_token: str = hex_token.get()

    assert isinstance(raw_hex_token, str)
    assert raw_hex_token == raw_lowercase_hex_token


def test_a_convert_to_str_of_a_hex_token(
    hex_token: HexToken, raw_lowercase_hex_token: str
) -> None:
    raw_hex_token: str = str(hex_token)

    assert raw_hex_token == hex_token.get()
    assert raw_hex_token == raw_lowercase_hex_token

from typing import Self, override

from pytest import fixture, raises

from libs import Token


@fixture
def token_wrapper() -> Token:
    class TokenWrapper(Token):

        @override
        def get(self: Self) -> str:
            return (
                super().get()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

    return TokenWrapper()


def test_disallow_of_a_creation_of_a_token_interface_instance() -> None:
    with raises(TypeError):
        _ = Token()  # pyright: ignore[reportAbstractUsage]  # type: ignore


def test_disallow_of_a_direct_using_of_a_get_method(
    token_wrapper: Token,
) -> None:
    with raises(NotImplementedError):
        _ = token_wrapper.get()

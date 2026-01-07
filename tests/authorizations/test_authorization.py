from typing import Self, override

from pytest import fixture, raises

from libs import Authorization


@fixture
def authorization_wrapper() -> Authorization:
    class AuthorizationWrapper(Authorization):

        @override
        def authorize(self: Self) -> bool:
            return (
                super().authorize()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

    return AuthorizationWrapper()


def test_disallow_of_a_creation_of_an_authorization_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = (
            Authorization()
        )  # pyright: ignore[reportAbstractUsage]  # type: ignore


def test_disallow_of_a_direct_using_of_an_authorize_method(
    authorization_wrapper: Authorization,
) -> None:
    with raises(NotImplementedError):
        _ = authorization_wrapper.authorize()

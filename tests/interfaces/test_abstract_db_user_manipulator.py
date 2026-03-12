from typing import Self, cast, override
from uuid import UUID

from pytest import fixture, raises
from pytest_mock import MockerFixture

from message_sender_telegram_bot.libs import Token, User
from message_sender_telegram_bot.libs.interfaces import (
    AbstractDBUserManipulator,
)


@fixture
def abstract_db_user_manipulator_wrapper() -> AbstractDBUserManipulator:
    class AbstractDBUserManipulatorWrapper(AbstractDBUserManipulator):
        @override
        def get(self: Self) -> User | None:
            return super().get()

        @override
        def create(self: Self) -> User:
            return super().create()

        @override
        def get_authorizing_status(self: Self) -> bool:
            return super().get_authorizing_status()

        @override
        def get_token(self: Self) -> Token | None:
            return super().get_token()

        @override
        def set_authorizing_status(self: Self, is_authorizing: bool) -> None:
            return super().set_authorizing_status(is_authorizing)

        @override
        def set_token(self: Self, token: Token) -> None:
            return super().set_token(token)

        @override
        def clear_token(self: Self) -> None:
            return super().clear_token()

        @override
        def get_owner_status(self: Self) -> bool:
            return super().get_owner_status()

    return AbstractDBUserManipulatorWrapper()


def test_disallow_of_creation_of_abstract_db_user_manipulator_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = AbstractDBUserManipulator()


def test_disallow_of_direct_using_of_get_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get()


def test_disallow_of_direct_using_of_create_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.create()


def test_disallow_of_direct_using_of_get_authorizing_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_authorizing_status()


def test_disallow_of_direct_using_of_get_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_token()


def test_disallow_of_direct_using_of_set_authorizing_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_authorizing_status(True)


def test_disallow_of_direct_using_of_set_token_method(
    mocker: MockerFixture,
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    token_class_mock = cast(
        type[Token],
        mocker.patch("message_sender_telegram_bot.libs.Token", autospec=True),
    )
    token_mock = token_class_mock(
        id_=UUID("1f1cdfde-6c8a-4e8b-82ed-147de2f265af"),
        token="TOKEN",
        user=None,
    )

    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_token(token_mock)


def test_disallow_of_direct_using_of_clear_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.clear_token()


def test_disallow_of_direct_using_of_get_owner_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_owner_status()

from typing import Self, override
from unittest.mock import patch

from pytest import fixture, raises

from message_sender_telegram_bot.libs import (
    AbstractDBUserManipulator,
    User,
    ValidToken,
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
        def get_valid_token(self: Self) -> ValidToken | None:
            return super().get_valid_token()

        @override
        def set_authorizing_status(self: Self, is_authorizing: bool) -> None:
            return super().set_authorizing_status(is_authorizing)

        @override
        def set_valid_token(self: Self, valid_token: ValidToken) -> None:
            return super().set_valid_token(valid_token)

        @override
        def clear_valid_token(self: Self) -> None:
            return super().clear_valid_token()

        @override
        def get_owner_status(self: Self) -> bool:
            return super().get_owner_status()

    return AbstractDBUserManipulatorWrapper()


def test_disallow_of_a_creation_of_a_abstract_db_user_manipulator_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = AbstractDBUserManipulator()


def test_disallow_of_a_direct_using_of_a_get_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get()


def test_disallow_of_a_direct_using_of_a_create_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.create()


def test_disallow_of_a_direct_using_of_a_get_authorizing_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_authorizing_status()


def test_disallow_of_a_direct_using_of_a_get_valid_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_valid_token()


def test_disallow_of_a_direct_using_of_a_set_authorizing_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_authorizing_status(True)


@patch("message_sender_telegram_bot.libs.ValidToken")
def test_disallow_of_a_direct_using_of_a_set_valid_token_method(
    valid_token_mock: ValidToken,
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_valid_token(
            valid_token_mock
        )


def test_disallow_of_a_direct_using_of_a_clear_valid_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.clear_valid_token()


def test_disallow_of_a_direct_using_of_a_get_owner_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_owner_status()

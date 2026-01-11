from typing import Self, override

from pytest import fixture, raises

from libs import AbstractDBUserManipulator, User


@fixture
def abstract_db_user_manipulator_wrapper() -> AbstractDBUserManipulator:
    class AbstractDBUserManipulatorWrapper(AbstractDBUserManipulator):

        @override
        def get(self: Self) -> User | None:
            return (
                super().get()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

        @override
        def create(self: Self) -> User:
            return (
                super().create()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

        @override
        def get_authorizing_status(self: Self) -> bool:
            return (
                super().get_authorizing_status()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

        @override
        def get_token(self: Self) -> str | None:
            return (
                super().get_token()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

        @override
        def set_authorizing_status(self: Self, is_authorizing: bool) -> None:
            return super().set_authorizing_status(  # pyright: ignore[reportAbstractUsage]  # type: ignore
                is_authorizing
            )

        @override
        def set_token(self: Self, token: str) -> None:
            return super().set_token(  # pyright: ignore[reportAbstractUsage]  # type: ignore
                token
            )

        @override
        def clear_token(self: Self) -> None:
            return (
                super().clear_token()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

    return AbstractDBUserManipulatorWrapper()


def test_disallow_of_a_creation_of_a_abstract_db_user_manipulator_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = (
            AbstractDBUserManipulator()
        )  # pyright: ignore[reportAbstractUsage]  # type: ignore


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


def test_disallow_of_a_direct_using_of_a_get_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.get_token()


def test_disallow_of_a_direct_using_of_a_set_authorizing_status_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_authorizing_status(True)


def test_disallow_of_a_direct_using_of_a_set_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.set_token("TOKEN")


def test_disallow_of_a_direct_using_of_a_clear_token_method(
    abstract_db_user_manipulator_wrapper: AbstractDBUserManipulator,
) -> None:
    with raises(NotImplementedError):
        _ = abstract_db_user_manipulator_wrapper.clear_token()

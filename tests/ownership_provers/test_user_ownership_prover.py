from unittest.mock import MagicMock, patch

from pytest import fixture

from libs import DBUserManipulator, UserOwnershipProver


@fixture
@patch(
    "libs.DBUserManipulator", get_owner_status=MagicMock(return_value=False)
)
def user_ownership_prover_without_ownership(
    db_user_manipulator_mock: DBUserManipulator,
) -> UserOwnershipProver:
    return UserOwnershipProver(db_user_manipulator_mock)


@fixture
@patch("libs.DBUserManipulator", get_owner_status=MagicMock(return_value=True))
def user_ownership_prover_with_ownership(
    db_user_manipulator_mock: DBUserManipulator,
) -> UserOwnershipProver:
    return UserOwnershipProver(db_user_manipulator_mock)


def test_a_prove_method_of_a_user_ownership_prover_without_ownership(
    user_ownership_prover_without_ownership: UserOwnershipProver,
) -> None:
    is_user_owner: bool = user_ownership_prover_without_ownership.prove()

    assert isinstance(is_user_owner, bool)
    assert not is_user_owner


def test_a_prove_method_of_a_user_ownership_prover_with_ownership(
    user_ownership_prover_with_ownership: UserOwnershipProver,
) -> None:
    is_user_owner: bool = user_ownership_prover_with_ownership.prove()

    assert isinstance(is_user_owner, bool)
    assert is_user_owner

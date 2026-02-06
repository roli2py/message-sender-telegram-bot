from typing import Self, override

from pytest import fixture, raises

from message_sender_telegram_bot.libs import OwnershipProver


@fixture
def ownership_prover_wrapper() -> OwnershipProver:
    class OwnershipProverWrapper(OwnershipProver):
        @override
        def prove(self: Self) -> bool:
            return super().prove()

    return OwnershipProverWrapper()


def test_disallow_of_a_creation_of_an_ownership_prover_instance() -> None:
    with raises(TypeError):
        _ = OwnershipProver()


def test_disallow_of_a_direct_using_of_a_prove_method(
    ownership_prover_wrapper: OwnershipProver,
) -> None:
    with raises(NotImplementedError):
        _ = ownership_prover_wrapper.prove()

from typing import Self, override

from pytest import fixture, raises

from libs import CooldownChecker


@fixture
def cooldown_checker_wrapper() -> CooldownChecker:
    class CooldownCheckerWrapper(CooldownChecker):

        @override
        def is_pass(self: Self) -> bool:
            return (
                super().is_pass()  # pyright: ignore[reportAbstractUsage]  # type: ignore
            )

    return CooldownCheckerWrapper()


def test_disallow_of_a_creation_of_an_cooldown_checker_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = (
            CooldownChecker()
        )  # pyright: ignore[reportAbstractUsage]  # type: ignore


def test_disallow_of_a_direct_using_of_an_is_pass_method(
    cooldown_checker_wrapper: CooldownChecker,
) -> None:
    with raises(NotImplementedError):
        _ = cooldown_checker_wrapper.is_pass()

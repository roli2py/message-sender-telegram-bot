from typing import Self, override

from pytest import fixture, raises

from libs import Sender


@fixture
def sender_wrapper() -> Sender:
    class SenderWrapper(Sender):

        @override
        def send(self: Self, data: str) -> None:
            return super().send(  # pyright: ignore[reportAbstractUsage]  # type: ignore
                data
            )

    return SenderWrapper()


def test_disallow_of_a_creation_of_a_sender_interface_instance() -> None:
    with raises(TypeError):
        _ = Sender()  # pyright: ignore[reportAbstractUsage]  # type: ignore


def test_disallow_of_a_direct_using_of_a_send_method(
    sender_wrapper: Sender,
) -> None:
    with raises(NotImplementedError):
        _ = sender_wrapper.send("DATA")

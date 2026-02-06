from typing import Self, override

from pytest import fixture, raises

from message_sender_telegram_bot.libs import DBItemGetter
from message_sender_telegram_bot.libs.database_tables import Base


@fixture
def db_item_getter_wrapper() -> DBItemGetter:
    class DBItemGetterWrapper(DBItemGetter):
        @override
        def get(self: Self) -> Base | None:
            return super().get()

    return DBItemGetterWrapper()


def test_disallow_of_a_creation_of_a_db_item_getter_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = DBItemGetter()


def test_disallow_of_a_direct_using_of_a_get_method(
    db_item_getter_wrapper: DBItemGetter,
) -> None:
    with raises(NotImplementedError):
        _ = db_item_getter_wrapper.get()

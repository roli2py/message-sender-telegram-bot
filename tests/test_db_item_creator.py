from typing import Self, override

from pytest import fixture, raises

from message_sender_telegram_bot.libs.interfaces import DBItemCreator
from message_sender_telegram_bot.libs.rdb.database_tables import Base


@fixture
def db_item_creator_wrapper() -> DBItemCreator:
    class DBItemCreatorWrapper(DBItemCreator):
        @override
        def create(self: Self) -> Base:
            return super().create()

    return DBItemCreatorWrapper()


def test_disallow_of_a_creation_of_a_db_item_creator_interface_instance() -> (
    None
):
    with raises(TypeError):
        _ = DBItemCreator()


def test_disallow_of_a_direct_using_of_a_create_method(
    db_item_creator_wrapper: DBItemCreator,
) -> None:
    with raises(NotImplementedError):
        _ = db_item_creator_wrapper.create()

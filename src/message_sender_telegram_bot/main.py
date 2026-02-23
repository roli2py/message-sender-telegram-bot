from __future__ import annotations

import re
from logging import getLogger
from typing import TYPE_CHECKING
from urllib.parse import SplitResult

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from .libs import Handlers, Helpers, Settings
from .libs.consts import Commands

if TYPE_CHECKING:
    from logging import Logger

    from sqlalchemy import Engine
    from sqlalchemy.orm import Session

logger: Logger = getLogger(__name__)

# Getting values from the environment variables
#
# Type checker throws errors about the missing arguments, but Pydantic
# anyway gets the values from the environment, so the error is
# suppressed
settings = Settings()  # type: ignore[missing-argument]

db_url = SplitResult(
    "mysql+mysqldb",
    (
        f"{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}"
    ),
    settings.db_name,
).geturl()

database_engine: Engine = create_engine(db_url, pool_pre_ping=True)
compiled_session: sessionmaker[Session] = sessionmaker(database_engine)

helpers = Helpers(
    settings.gmail_smtp_login,
    settings.gmail_smtp_password,
    settings.email_from_addr,
    settings.email_to_addr,
    compiled_session,
)
handlers = Handlers(compiled_session, helpers)


async def post_init(_) -> None:
    logger.info("Started")


# Creating an app and adding handlers
app = (
    ApplicationBuilder()
    .token(settings.telegram_token)
    .post_init(post_init)
    .build()
)

start_command_handler = CommandHandler(Commands.START, handlers.start)
admin_command_handler = CommandHandler(
    Commands.ADMIN, handlers.show_admin_panel
)
cancel_command_handler = CommandHandler(Commands.CANCEL, handlers.cancel)
unknown_command_handler = MessageHandler(
    filters.COMMAND, handlers.notify_about_unknown_command
)
token_generation_request_handler = CallbackQueryHandler(
    handlers.generate_token, re.compile(r"^generate_token$")
)
send_message_handler = CallbackQueryHandler(
    handlers.send, re.compile(r"^message_confirmation,true,[0-9]{0,19}$")
)
cancel_message_handler = CallbackQueryHandler(
    handlers.cancel, re.compile(r"^message_confirmation,false,[0-9]{0,19}$")
)
message_handler = MessageHandler(filters.TEXT, handlers.handle_message)

app.add_handler(start_command_handler)
app.add_handler(admin_command_handler)
app.add_handler(cancel_command_handler)
app.add_handler(unknown_command_handler)
app.add_handler(token_generation_request_handler)
app.add_handler(send_message_handler)
app.add_handler(cancel_message_handler)
app.add_handler(message_handler)

if __name__ == "__main__":
    app.run_polling()

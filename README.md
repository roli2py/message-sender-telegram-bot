# Message Sender — Telegram Bot

A telegram bot that sends messages to the different platforms.

## Running

1. Clone the repository:
```bash
git clone https://github.com/roli2py/message-sender-telegram-bot
```

2. Navigate to the repository
```bash
cd message-sender-telegram-bot
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Fill a `sqlalchemy.url` property in the `alembic.ini` file:
```ini
# ...
# replace the placeholders to appropriate data
sqlalchemy.url = mysql+mysqldb://user:pass@host:port/dbname
# ...
```

5. Migrate the database by `alembic`:
```bash
alembic upgrade head
```

5. Duplicate the `example.env` file and name it to `.env`:
```bash
cp example.env .env
```

6. Fill the `.env` file with the appropriate data

7. Export the `.env` file to your environment:
```bash
set -a && source .env && set +a
```
Reference: https://gist.github.com/mihow/9c7f559807069a03e302605691f85572

8. Navigate to the project's package:
```bash
cd src/message_sender_telegram_bot
```

9. Run the `main.py` file:
```bash
python3 main.py
```

## Developing

1. Clone the repository:
```bash
git clone https://github.com/roli2py/message-sender-telegram-bot
```

2. Navigate to the repository
```bash
cd message-sender-telegram-bot
```

3. Install the project's package in an editable mode with the `dev` deps:
```bash
pip install -e .[dev]
```

4. Start to develop :)

5. After the develop, start `make` to format and test the project:
```bash
make
```

6. To run the project, see "[Running](#running)" from a fourth to ninth clause.

If you want, you can start the specific action:
```bash
make test
```

Available targets:
1. `all` — Invokes all targets. Invoked by default, if `make` is started without the target.
2. `format` — Formats the project by `isort` and `black`.
3. `test` — Starts the unittests by `pytest`.


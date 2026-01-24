# Message Sender — Telegram Bot

A telegram bot that sends messages to the different platforms.

From the receiver's (that is, a bot's owner's) side, it helps to concetrate only on the important messages and to not worry, that you miss something. From the sender's (for example, friend's) side, it gives a handy Telegram interface that simplify a using of the message sender.

![Work Scheme](assets/images/work-scheme.png)

## Running

Before reading this chapter, ensure that you have an installed and set up [MariaDB](https://mariadb.com) or [MySQL](https://www.mysql.com).

Steps to set up the project:
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
6. Duplicate the `example.env` file and name it to `.env`:
    ```bash
    cp example.env .env
    ```
7. Fill the `.env` file with the appropriate data.
8. Export the `.env` file to your environment:
    ```bash
    set -a && source .env && set +a
    ```
    Reference: https://gist.github.com/mihow/9c7f559807069a03e302605691f85572
9. Navigate to the project's package:
    ```bash
    cd src/message_sender_telegram_bot
    ```
10. Run the `main.py` file:
    ```bash
    python3 main.py
    ```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Code of Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

See [`LICENSE`](LICENSE).


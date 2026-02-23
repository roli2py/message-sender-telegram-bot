from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MESSAGE_SENDER_TELEGRAM_BOT_"
    )

    telegram_token: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    gmail_smtp_login: str
    gmail_smtp_password: str
    email_from_addr: str
    email_to_addr: str

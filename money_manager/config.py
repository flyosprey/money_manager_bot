import pytz
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

TIMEZONE_KYIV = pytz.timezone("Europe/Kyiv")  # MoneyManager handle only UTC time!
TIMEZONE_UTC = pytz.timezone("UTC")


class BotConfig(BaseSettings):
    default_token: str = Field(..., description="Default bot token")


class RedisConfig(BaseSettings):
    url: str = Field(..., description="Redis url")


class PostgresConfig(BaseSettings):
    url: str = Field(..., description="Redis url")


class Config(BaseSettings):
    dsn: str = Field(..., description="DSN of the application")
    secret_key: SecretStr = Field(..., description="Secret Key")
    is_test: bool = Field(False, description="Test mode")
    bot_conf: BotConfig = Field(..., description="Bot Config")
    redis: RedisConfig = Field(..., description="Redis Config")
    postgres: PostgresConfig = Field(..., description="Postgres Config")

    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"
        extra = "ignore"


config = Config()

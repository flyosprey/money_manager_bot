from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class MonoConfig(BaseSettings):
    base_url: str = Field(..., description="Monobank base url")
    transaction_period: int = Field(
        7200, description="Period for get transaction til now"
    )


class WalletAppConfig(BaseSettings):
    base_url: str = Field(..., description="WalletApp base url")


class BotConfig(BaseSettings):
    default_token: str = Field(..., description="Default bot token")


class RedisConfig(BaseSettings):
    url: str = Field(..., description="Redis url")


class PostgresConfig(BaseSettings):
    url: str = Field(..., description="Redis url")


class Config(BaseSettings):
    dsn: str = Field(..., description="DSN of the application")
    secret_key: SecretStr = Field(..., description="Secret Key")
    monobank: MonoConfig = Field(..., description="Monobank Config")
    walletapp: WalletAppConfig = Field(..., description="WalletApp Config")
    bot_conf: BotConfig = Field(..., description="Bot Config")
    redis: RedisConfig = Field(..., description="Redis Config")
    postgres: PostgresConfig = Field(..., description="Postgres Config")

    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"
        extra = "ignore"


config = Config(_env_file=".env")

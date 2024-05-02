from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class MonoConfig(BaseSettings):
    base_url: str = Field(..., description="Monobank base url")


class WalletAppConfig(BaseSettings):
    base_url: str = Field(..., description="WalletApp base url")


class Config(BaseSettings):
    secret_key: SecretStr = Field(..., description="Secret Key")
    monobank: MonoConfig = Field(..., description="Monobank Config")
    walletapp: WalletAppConfig = Field(..., description="WalletApp Config")

    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"


settings = Config(_env_file=".env")
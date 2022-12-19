from pathlib import Path

from pydantic import BaseSettings

CONFIG_FILE = Path('../.env').as_posix() if Path('../.env').exists() else None


class EnvironmentEnum(str):
    LOCAL = 'LOCAL'
    STAGE = 'STAGE'
    PROD = 'PROD'


class LoggingLevelEnum(str):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'


class AppConfig(BaseSettings):
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.LOCAL
    APP_NAME: str = 'kursach'

    LOG_LEVEL: LoggingLevelEnum = LoggingLevelEnum.DEBUG

    POSTGRES_DSN = 'postgresql+asyncpg://app:123qwe@localhost:5432/postgres'
    SECRET_TOKEN_KEY = b'8ffsZ-qAz7dJtONx3y4Rsmt7tlrOfT28IlJmlVyOBhs='
    JWT_TOKEN_EXPIRATION_TIME = 15

    class Config:
        use_enum_values = True
        env_file = CONFIG_FILE


config: AppConfig = AppConfig(_env_file_encoding='utf-8')

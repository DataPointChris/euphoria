import os
from dataclasses import dataclass, field


@dataclass
class FlaskSettings:
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ENV: str = os.getenv('ENVIRONMENT')


@dataclass
class PostgresSettings:
    POSTGRES_URI: str = os.getenv('POSTGRES_URI')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DATABASE_URI: str = (
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URI}:5432/ichrisbirch'
    )


@dataclass
class SQLAlchemySettings:
    SQLALCHEMY_ECHO: bool = True
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = ""


@dataclass
class MongoDBSettings:
    MONGODB_URI: str = os.getenv('MONGODB_URI')
    MONGODB_USER: str = os.getenv('MONGODB_USER')
    MONGODB_PASSWORD: str = os.getenv('MONGODB_PASSWORD')
    MONGODB_DATABASE_URI: str = f'mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_URI}/ichrisbirch?retryWrites=true&w=majority'


@dataclass
class DynamoDBSettings:
    DYNAMODB_URL: str = os.getenv('DYNAMODB_URL')
    DYNAMODB_USER: str = os.getenv('DYNAMODB_USER')
    DYNAMODB_PASSWORD: str = os.getenv('DYNAMODB_PASSWORD')
    DYNAMODB_DATABASE_URI: str = os.getenv('DYNAMODB_DATABASE_URI')


@dataclass
class SQLiteSettings:
    SQLITE_DATABASE_URI: str = os.getenv('SQLITE_DATABASE_URI')


@dataclass
class LoggingSettings:
    LOG_PATH: str = f"{os.getenv('OS_PREFIX')}{os.getenv('LOG_PATH')}"
    LOG_FORMAT: str = os.getenv('LOG_FORMAT')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL')


@dataclass
class Settings:
    NAME: str = 'ichrisbirch.com'
    DB_SCHEMAS: list[str] = field(default_factory=lambda: ['apartments', 'box_packing', 'habits'])
    API_URL: str = os.getenv('API_URL')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT')
    OS_PREFIX: str = os.getenv('OS_PREFIX')

    flask = FlaskSettings()
    sqlite = SQLiteSettings()
    mongodb = MongoDBSettings()
    dynamodb = DynamoDBSettings()
    postgres = PostgresSettings()
    sqlalchemy = SQLAlchemySettings()
    logging = LoggingSettings()
    sqlalchemy.SQLALCHEMY_DATABASE_URI = postgres.POSTGRES_DATABASE_URI
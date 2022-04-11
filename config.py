import os
import dotenv

dotenv.load_dotenv()


class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    TESTING = False
    DEVELOPMENT = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_SQLALCHEMY_DATABASE_URI')
    DYNAMODB_DATABASE_URI = os.environ.get('DEV_DYNAMODB_DATABASE_URI')
    MONGODB_DATABASE_URI = os.environ.get('DEV_MONGODB_DATABASE_URI')
    SQLITE_DATABASE_URI = os.environ.get('DEV_SQLITE_DATABASE_URI')


class TestingConfig(Config):
    TESTING = True
    DEVELOPMENT = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_SQLALCHEMY_DATABASE_URI')
    DYNAMODB_DATABASE_URI = os.environ.get('TEST_DYNAMODB_DATABASE_URI')
    MONGODB_DATABASE_URI = os.environ.get('TEST_MONGODB_DATABASE_URI')
    SQLITE_DATABASE_URI = os.environ.get('TEST_SQLITE_DATABASE_URI')


class ProductionConfig(Config):
    TESTING = False
    DEVELOPMENT = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_SQLALCHEMY_DATABASE_URI')
    DYNAMODB_DATABASE_URI = os.environ.get('PROD_DYNAMODB_DATABASE_URI')
    MONGODB_DATABASE_URI = os.environ.get('PROD_MONGODB_DATABASE_URI')
    SQLITE_DATABASE_URI = os.environ.get('PROD_SQLITE_DATABASE_URI')
class BaseConfig:
    SECRET_KEY = 'change-me'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

class TestingConfig(BaseConfig):
    TESTING = True


import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingCongig(Config):
    Testing = True


class ProductionConfig(Config):
    pass


Config = {
    'development': DevelopmentConfig,
    'testing': TestingCongig,
    'production': ProductionConfig,
    'default': DevelopmentConfig

}





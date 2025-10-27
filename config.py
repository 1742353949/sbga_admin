#config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'some string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    LOCAL_DB = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    '''开发环境配置'''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')

class TestingConfig(Config):
    '''测试环境配置'''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 123

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 123

class MysqlConfig(Config):
    if Config.LOCAL_DB:
        CHARSET = 'utf8'
        USER = 'kmlskj'
        PASSWORD = 'kmlskj@123'
        DB = "kmlskj_bs_data"
        HOST = "127.0.0.1"
        PORT = 3306
    else:
        CHARSET = 'utf8'
        USER = 'kmlskj'
        PASSWORD = 'kmlskj@123'
        DB = "fd_wd_ga_data"
        HOST = "132.232.137.173"
        PORT = 3306
    # if Config.LOCAL_DB:
    #     CHARSET = 'utf8'
    #     USER = 'kmlskj'
    #     PASSWORD = 'kmlskj@123'
    #     DB = "kmlskj_bs_data"
    #     HOST = "127.0.0.1"
    #     PORT = 3306
    # else:
    #     CHARSET = 'utf8'
    #     USER = 'wd_data'
    #     PASSWORD = 'wd_data@1631'
    #     DB = "wd_data"
    #     HOST = "106.60.13.217"
    #     PORT = 33306

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

class RabbitmqConfig(Config):
    USER="user"
    PASSWORD="password"
    HOST = "IP"
    PROT= "port"

class WebsockConfig(Config):
    URL="ws://124.71.144.85:5001"

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig,
    'mysql':MysqlConfig,
    "ws":WebsockConfig
}#用一个字典来统合地给出所有配置
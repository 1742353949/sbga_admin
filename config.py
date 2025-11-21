#config.py
import os
import secrets

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY') or 'some string'
    SECRET_KEY = os.getenv('SECRET_KEY')  or secrets.token_hex(16)
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
        USER = 'jin'
        PASSWORD = 'Jin2025!'
        DB = "wd_data"
        HOST = "127.0.0.1"
        PORT = 3306
    else:
        CHARSET = 'utf8'
        USER = 'kmlskj'
        PASSWORD = 'kmlskj@123'
        DB = "sys_test"
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

# class qlyConfig(Config):
#     APPID = "6c087dbb5a074c13a011befc6b835fe5"
#     SECRET = "qWSk4oQ5f8UHKXQO"
#     RSA_PRIVATE_KEY = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAIFnG+jvrnNbFzXArfG/dFH38n0p5pg9P3chIFn8MEvXHNDcdAa86SG35kghMwM37FKRq5NoTs0j81RIr7pqilF4pLqK6ZhDTjCXp5UK3zT4vnNecUJETSE/FgKtMeHsf9hv8zFmbqL0R/Ycgj+ZJ/Pr8Kuw/zV014bpOMLAi4hFAgMBAAECgYBaf8wLKqUs1AX1d92u9qDZOrkCRC2bRyp9nFNN24vDXpwujh8vHytEg6Kvy1gr5g6G6I3AN/D0kzH4PiV4EE7PERAIV2LfXMsgX7D949xz7M4OTcCXUDQCHde4EpIxvgZzRONYgDWD/gguc5b3dKcy9qAzv80To2gL+VFDvi24gQJBALq+/KW6Kk4O2wpYHcrNnFAEJKh7WI7dKUb5cfSr0y49rM9cY89BXrPcwqlB/spfkdTKQtsaNY1QPszjCIo13BECQQCxZCc9F57X0iftFK0wZO5o7oZGcCMk77crI/X4h9IhJurw8q+WoR4HIlqVJXLdsSlMoQo1RuRayjs+21LXXSz1AkBQmDR5Ycr4PTkTUcwpxmr7rY4UmIczwQcbdnRT4AQYJM38ACejPtccUN5CJhVMScqqR1BrNvh9sHAqBKGe5HfBAkBrlPP/Jw4ckcXJENsgGHZGiTJCEcweoIsTzNFmEukrVfDyhBxdXAVcCkepYHbTYJhNcvU/7mibbz6TFmydVFLpAkBdXdw4n+a5ZVPVsGmyT1tVxxCryJlwl2FAePuEtF9d847Q1Nz62A9u38/Xxx9SxWUIIE5AIGBewdtdDJaLf8Rh"
#     BASE_ADDRESS = "https://open.andmu.cn"

class qlyConfig(Config):
    APPID = "5c7212bdfa854034a5c6d5972973bd92"
    SECRET = "Ogs3cYzZe7ZINFLu"
    RSA_PRIVATE_KEY = "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAIRWB/yuw/r//WBlI1x/q+dhwGhGkTTBqlr0jMds7sAJphR53wUEE3n6euITdr+oTcyXI1zio+nAB77VuQzPu9JFmN1B8tfIYrXDekZZk6YxVJqJpMCJFSVUWVcmyFmxX42PsquYPwkZaTyjKQmrBLAtZ8UBd+lH2yZs7bwbKju3AgMBAAECgYB/23sWCGhzXtcYRj83BGc7Q7eZR+zNUvvbqwFFQJsf0XKzv9fYycpjhL0rJnEJ1XttWu0gthx2IEGbgHSsyxwENbdOGJrg6b7usmx1WGClL0qP9/BZjVmmGICc4w886s9g5dU4hXWJZu0RDvK6HEOu3JIh9j/1qr+Ug09JyrQuuQJBAL6Bnmb3B5y6U1KUNX0AvPSL+p6NbfkmnZ8uw7GL06BJLxiS0v1+WSebe7YKQG195sOEwo3XawncUaP8qrd0PhUCQQCx1N89A83a++QuGnPERXToajsyUuPwNiBLcUhmjkLz0Zo6eHSfNTY0CuyxH2mbVWBjFh+Sblb9Wsjau1TslFGbAkEAonARachPJFM3wtz+8rRTac2Fh/YeBGjp05ZjZJtOeoiMcM6Yu28lhAEurhz1rKbCwooL/jflXAYRUtuZkU27tQJAJQRUu9Sw4yaP5vDmrDJxFXgXfnA2tmft7QZVtdNjKHG3EvjD/egLsmWbw3rwdr8c40NVqxuAzBg7uxxHnz94hQJAe+KKoiR3gfktyH/GFx5YtomVe59Cwj2YDHLo6zo2LuPeApkQ1t7ld4UeWKP08noCfF1Ov+vxRyev0PAlqyH7kQ=="
    BASE_ADDRESS = "https://open.andmu.cn"

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig,
    'mysql':MysqlConfig,
    "ws":WebsockConfig,
    "qly":qlyConfig
}#用一个字典来统合地给出所有配置
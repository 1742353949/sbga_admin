from flask import Flask

class Config:
    DEBUG = True
    SECRET_KEY = 'mysecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mydatabase.db'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)

    from ... import routes
    app.register_blueprint(routes.bp)

    return app
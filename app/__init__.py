from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from config import config
from app.wsClient.wsClient import WebSocketClient

db = SQLAlchemy()

def create_app():
    app = Flask(__name__,
                static_url_path="/static"
                # ,template_folder="/views"
                )
    #跨域处理
    CORS(app)
    #导入配置文件
    app.config.from_object(config)
    # db.init_app(app)
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.qly import qly
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(qly)
    return app

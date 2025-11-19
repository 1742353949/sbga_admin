from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from config import config
from app.wsClient.wsClient import WebSocketClient
import json

# 自定义JSON编码器，确保正确处理Unicode字符
class UnicodeJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        return super().encode(obj)

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
    
    # 确保JSON响应正确处理Unicode字符
    app.config['JSON_AS_ASCII'] = False
    # 在Flask 3.x中，通过json.provider设置ensure_ascii属性
    app.json.ensure_ascii = False  # type: ignore
    
    # 设置自定义JSON编码器 (适配Flask 3.x)
    # Flask 3.x中不能再直接设置app.json.encoder，而是应该使用json.provider
    # 由于只需要确保Unicode字符正确处理，我们已经设置了ensure_ascii=False，这个就足够了

    #公共帮助路由
    from app.routes.Common.HelperRoute import help
    app.register_blueprint(help)

    # db.init_app(app)
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.qly import qly
    from app.routes.sbga_routes import Sbga
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(qly)
    app.register_blueprint(Sbga)

    # 管理后台
    from app.routes.Admin.AdminRoute import admin    
    app.register_blueprint(admin)
    # json管理
    from app.routes.Admin.jsonRoute import jsonmanage
    app.register_blueprint(jsonmanage)
     # API管理工具
    from app.routes.Admin.apiRoute import apimanager
    app.register_blueprint(apimanager)    
    # 注册导入功能路由
    from app.routes.Admin.ImportRoute import import_bp
    app.register_blueprint(import_bp)
    
    # 设置静态文件访问
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return app.send_static_file(filename)

    return app
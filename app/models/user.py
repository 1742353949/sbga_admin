#用户模型
from app import db
from app.helper.helper import gen_md5

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        """设置用户密码"""
        self.password_hash = gen_md5(password)
        
    def check_password(self, password):
        """验证用户密码"""
        return self.password_hash == gen_md5(password)
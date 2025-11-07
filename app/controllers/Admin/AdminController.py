from flask import render_template,request
from app.helper.helper import *
from app.models.base_db import MySQLHelper  # 导入 MySQLHelper


class AdminController():
    def __init__(self) -> None:
        super().__init__()
    
    def index(self):
        return render_template('Admin/index.html')
    
    def login(self):
        username = get_param_by_str('username')
        password = get_param_by_str('password')
        return render_template('Admin/login.html')

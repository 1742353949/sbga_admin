#认证相关路由
from flask import Blueprint, render_template, request, redirect, url_for
from config import *

#导入控制器
from app.controllers.Admin.AdminController import AdminController

#定义蓝图
admin = Blueprint('admin', __name__,url_prefix='/admin')

#定义控制器
c_admin = AdminController()

@admin.route('/index', methods=['GET','POST'])
def index():
    return c_admin.index()

@admin.route('/login', methods=['GET','POST'])
def login():
    return c_admin.login()
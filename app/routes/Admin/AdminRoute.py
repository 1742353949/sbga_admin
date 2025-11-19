#认证相关路由
from flask import Blueprint, render_template, request, redirect, url_for
from config import *

#导入控制器
from app.controllers.Admin.AdminController import AdminController

#定义蓝图
admin = Blueprint('admin', __name__,url_prefix='/admin')

#定义控制器
c_admin = AdminController()

@admin.route('/Demo/<path:url>', methods=['GET','POST'])
def demo(url):
    ishtml = url.find('.html')
    if ishtml != -1:
        return render_template('Demo/'+url)
    else:
        #js css 访问
        from flask import send_from_directory
        import os
        static_dir = os.path.join(os.getcwd(), 'app/static')
        print(static_dir)
        return send_from_directory(static_dir, url)
        
@admin.route('', methods=['GET','POST'])
def main():
    return c_admin.index()

@admin.route('/index', methods=['GET','POST'])
def index():
    return c_admin.index()

@admin.route('/login', methods=['GET','POST'])
def login():
    return c_admin.login()

@admin.route('/SBGA/jsonmanage', methods=['GET','POST'])
def SBGA_jsonmanage():
    return render_template('Admin/SBGA/jsonmanage.html')

@admin.route('/SBGA/apimanage', methods=['GET','POST'])
def SBGA_apimanage():
    return render_template('Admin/SBGA/apimanage.html')

@admin.route('/SBGA/upload', methods=['GET','POST'])
def SBGA_upload():
    return render_template('Admin/SBGA/upload.html')

@admin.route('/SBGA/ImportManager', methods=['GET','POST'])
def SBGA_ImportManager():
    return render_template('Admin/SBGA/ImportManager.html')
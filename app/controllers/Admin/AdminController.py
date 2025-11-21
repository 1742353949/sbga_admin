from flask import render_template,request,flash,redirect,url_for,session
from app.helper.helper import *
from app.models.base_db import MySQLHelper  # 导入 MySQLHelper
from app.models.user import User
import hashlib

class AdminController(MySQLHelper):
    def __init__(self) -> None:
        super().__init__()
        self._tbname="users"
    
    def index(self):
        # 验证会话：未登录则跳转回登录页
        if 'username' not in session:
            return redirect(url_for('login'))
        # 已登录：渲染后台页面（传递用户名给前端）
        #return f"欢迎 {session['username']} 进入后台管理系统！"
        return render_template('Admin/main.html')
    
    def login(self):
        if request.method == 'POST':
            # 1. 获取前端login.html表单提交的用户名和密码
            username = request.form.get('username', '').strip()  # 去空格，防空输入
            password = request.form.get('password', '').strip()
            captcha = request.form.get('captcha', '').strip()

            # 2. 基础校验（避免无效数据库查询）
            if not username or not password:
                return render_template('Admin/login.html', error_msg="用户名或密码不能为空")
            
            # 3. 验证验证码（这里只是示例，实际应有验证码生成和验证机制）
            # if not self.verify_captcha(captcha):
            #     return render_template('Admin/login.html', error_msg="验证码错误")

            # 4. 查询用户并验证密码（注意：数据库中存储的是明文密码）
            sql = f"SELECT id, username, password_hash FROM {self._tbname} WHERE username=%s"
            result = self.execute_query(sql, (username,))
            
            if result and len(result) > 0:
                user_data = result[0]
                # 直接比较明文密码（因为数据库中存储的是明文）
                if user_data['password_hash'] == password:
                    # 登录成功，设置 session
                    session['user_id'] = user_data['id']
                    session['username'] = user_data['username']
                    return redirect(url_for('admin.index'))
            
            # 登录失败
            return render_template('Admin/login.html', error_msg="用户名或密码错误")
                
        return render_template('Admin/login.html')

    def logout(self):
        # 清除session
        session.clear()
        return redirect(url_for('admin.login'))
    # def login(self):
    #     username = get_param_by_str('username')
    #     password = get_param_by_str('password')
    #     return render_template('Admin/login.html')
    
    

    # def login(self):
    #     # sql=f'SELECT username ,password_hash FROM {self._tbname}' 
    #     # result = self.execute_query(sql) 
      
    # #   if request.method == 'POST':
    # #     # 1. 获取前端login.html表单提交的用户名和密码
    # #     input_username = request.form.get('username', '').strip()  # 去空格，防空输入
    # #     input_password = request.form.get('password', '').strip()

    # #     # 2. 基础校验（避免无效数据库查询）
    # #     if not input_username or not input_password:
    # #         return render_template('login.html', error_msg="用户名或密码不能为空")
      
    #     # if request.method == 'POST':
    #     #     username = request.form.get('username')
    #     #     password = request.form.get('password')
    #     #     captcha = request.form.get('captcha')
            
    #     #     # 验证验证码（简化处理，实际项目中需要实现验证码验证逻辑）
    #     #     # if not self.verify_captcha(captcha):
    #     #     #     flash('验证码错误')
    #     #     #     return render_template('Admin/login.html')
            
    #     #     # 查询用户
    #     #    # user = User.query.filter_by(username=username).first()
            
    #     #     # 验证用户和密码
    #     #     if user and user.check_password(password):
    #     #         # 登录成功，设置 session
    #     #         session['user_id'] = user.id
    #     #         session['username'] = user.username
    #     #         return redirect(url_for('admin.index'))
    #     #     else:
    #     #         flash('用户名或密码错误')
                
    #     return render_template('Admin/login.html')

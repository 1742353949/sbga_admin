#认证相关路由
from flask import Blueprint, render_template, request, redirect, url_for

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/register')
def register():
    return render_template('register.html')
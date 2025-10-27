from flask import render_template
from app.models.Common_DB import CommonDB


staticIP= "http://132.232.137.173:8001"
_commonDB = CommonDB()
# 处理 /index 路由的函数
def index():
    # 这里可以进行数据处理和获取
    return render_template('OpenLayer/index.html')

def rl_index():
    return render_template('OpenLayer/rl_index.html')

def bs_mg():
    return render_template('OpenLayer/bs_mg.html')

def ExportExecl():
    return render_template('Helper/ExportExecl.html')

def sqlQuery(sql):
    return _commonDB.sqlQuery(sql)

def sqlUpdate(sql):
    return _commonDB.sqlUpdate(sql)






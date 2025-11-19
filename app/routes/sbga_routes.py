from flask import Blueprint, jsonify,request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.helper.helper import *
import json
#导入控制器

from app.controllers.SbgaController import SbgaController
#注册蓝图
Sbga=Blueprint('Sbga', __name__)

#创建控制器实例
c_sbga = SbgaController()

# #通过id查询人员信息
# @Sbga.route('/ry',methods=['GET','POST'])
# def ry():
#     method=request.method
#     if method=='POST':
#         body=request.get_json()
#         id=body.get('id')
#     else:
#         id=request.args.get('id')
#     data=c_sbga.get_wdybss_by_id(id)
        
#     return jsonify(data)
    
# 统一接口处理所有查询需求
@Sbga.route('/ry/query', methods=['GET', 'POST'])
def ryQuery():
    """
    统一查询接口，通过action参数区分不同操作：
    1. action=count - 查询总人数
    2. action=sex_count - 按性别查询人数
    3. action=sex_statistics - 查询所有性别统计信息
    4. action=all - 查询总人数、男性人数、女性人数的汇总信息
    5. action=list - 分页查询人员列表
    """
    method = request.method
    action = None
    page = 1
    page_size = 100
    
    if method == 'POST':
        body = request.get_json()
        action = body.get('action', 'list')
        page = int(body.get('page', 1))
        page_size = int(body.get('page_size', 100))
        sex = body.get('sex')
    else:
        action = request.args.get('action', 'list')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 100))
        sex = request.args.get('sex')
    
    # 限制每页最大条数为100
    page_size = min(page_size, 100)
    
    # 根据action执行不同操作
    if action == 'count':
        # 查询总人数
        data = c_sbga.get_wdybss_count()
    elif action == 'sex_count':
        # 按性别查询人数
        if not sex:
            return jsonify({"error": "Missing sex parameter"}), 400
        data = c_sbga.get_wd_ybss_sex_count(sex)
    elif action == 'sex_statistics':
        # 查询所有性别统计信息
        data = c_sbga.get_wd_ybss_all_sex_count()
    elif action == 'all':
        # 查询总人数、男性人数、女性人数的汇总信息
        total_count_data = c_sbga.get_wdybss_count()
        #sex_statistics=c_sbga.get_wd_ybss_all_sex_count()
        male_count_data = c_sbga.get_wd_ybss_sex_count('男')
        female_count_data = c_sbga.get_wd_ybss_sex_count('女')
        #print(total_count_data)
     
        
        summary_data = {
            "total": total_count_data["total_count"],
            #"sex_statistics":sex_statistics["sex_statistics"],
            "male": male_count_data["count"],
            "female": female_count_data["count"]
        }
        data = summary_data
    elif action == 'list':
        # 分页查询人员列表
        if sex:
            data = c_sbga.get_wd_ybss_list_by_sex(sex, page, page_size)
        else:
            data = c_sbga.get_wd_ybss_list(page, page_size)
    else:
        # 默认返回人员列表
        data = c_sbga.get_wd_ybss_list(page, page_size)
    
    return jsonify(data)

# # 总人数查询
# @Sbga.route('/ryCount')
# def ryCount():
#     data=c_sbga.get_wdybss_count()
#     return jsonify(data)
# #性别查询
# @Sbga.route('/ry/sex',methods=['GET','POST'])
# def rySex():
#     method=request.method
#     if method=='POST':
#         body=request.get_json()
#         sex=body.get('sex')
#     else:
#         sex=request.args.get('sex')
#     data=c_sbga.get_wd_ybss_sex_count(sex)
#     return jsonify(data)
    
# # 分页查询所有人员信息
# @Sbga.route('/ry/list', methods=['GET', 'POST'])
# def ryList():
#     method = request.method
#     if method == 'POST':
#         body = request.get_json()
#         page = int(body.get('page', 1))
#         page_size = int(body.get('page_size', 100))
#     else:
#         page = int(request.args.get('page', 1))
#         page_size = int(request.args.get('page_size', 100))
    
#     # 限制每页最大条数为100
#     page_size = min(page_size, 100)
    
#     data = c_sbga.get_wd_ybss_list(page, page_size)
#     return jsonify(data)

# # 根据性别分页查询人员信息
# @Sbga.route('/ry/list/sex', methods=['GET', 'POST'])
# def ryListBySex():
#     method = request.method
#     if method == 'POST':
#         body = request.get_json()
#         sex = body.get('sex')
#         page = int(body.get('page', 1))
#         page_size = int(body.get('page_size', 100))
#     else:
#         sex = request.args.get('sex')
#         page = int(request.args.get('page', 1))
#         page_size = int(request.args.get('page_size', 100))
    
#     # 限制每页最大条数为100
#     page_size = min(page_size, 100)
    
#     data = c_sbga.get_wd_ybss_list_by_sex(sex, page, page_size)
#     return jsonify(data)
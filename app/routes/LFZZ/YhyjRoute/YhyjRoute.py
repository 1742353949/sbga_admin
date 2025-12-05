################################################################################
# 模块名：YhyjRoute
# 功能：联防智治平台隐患预警模块路由
# 作者：jkf
# 时间：2025-12-04
##########

from flask import Blueprint, jsonify,request
from app.helper.helper import *
#导入控制器
from app.controllers.LFZZ.YhyjController.EcyjController import EcyjController

# 创建Flask蓝图，命名为'ecyj'，URL前缀为'/ecyj'，统一管理预警相关接口路由
lfzz = Blueprint('lfzz', __name__, url_prefix='/lfzz')

#创建控制器实例
c_ecyj = EcyjController()

@lfzz.route('/process_hist_data', methods=['GET'])
def process_hist_data():
    """
    处理hist表数据的API接口（原有注释保留）
    对外提供GET请求接口，触发hist数据与info_temp的合并处理逻辑
    :return: JSON响应 - 处理成功返回结果，失败返回错误信息和500状态码
    """
    # try:
    #     # 调用数据处理核心方法
    #     result = yddr()
    #     return jsonify(result)  # 返回成功响应
    # except Exception as e:
    #     # 捕获异常，返回错误信息和500服务器错误状态码
    #     print(f"❌ 接口处理异常：{str(e)}")
    #     return jsonify({"error": str(e)}), 500
    c_ecyj.yddr()
    # c_ecyj.yrdd()
    # c_ecyj.ycdq()
    c_ecyj.yqdc()
    
    
    return '成功' # 返回成功响应
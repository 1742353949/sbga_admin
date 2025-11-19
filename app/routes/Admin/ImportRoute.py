from flask import Blueprint, request, jsonify, render_template
from app.controllers.Admin.ImportController import ImportController
import os

# 创建蓝图
import_bp = Blueprint('import', __name__)

# 初始化控制器
import_controller = ImportController()


def make_unicode_response(data):
    """
    创建正确处理Unicode字符的响应
    """
    response = jsonify(data)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@import_bp.route('/import_manager')
def import_manager():
    """
    导入管理页面
    """
    return render_template('Admin/SBGA/ImportManager.html')


@import_bp.route('/api/get_tables', methods=['GET'])
def get_tables():
    """
    获取数据库中所有表
    """
    result = import_controller.get_tables()
    return make_unicode_response(result)


@import_bp.route('/api/get_table_structure/<table_name>', methods=['GET'])
def get_table_structure(table_name):
    """
    获取表结构信息
    
    Args:
        table_name (str): 表名
    """
    result = import_controller.get_table_structure(table_name)
    return make_unicode_response(result)


@import_bp.route('/api/upload_file', methods=['POST'])
def upload_file():
    """
    上传文件
    """
    if 'file' not in request.files:
        return make_unicode_response({"code": 400, "msg": "没有上传文件"})
    
    file = request.files['file']
    if file.filename == '':
        return make_unicode_response({"code": 400, "msg": "未选择文件"})
    
    result = import_controller.upload_file(file)
    return make_unicode_response(result)


@import_bp.route('/api/preview_file_data', methods=['POST'])
def preview_file_data():
    """
    预览文件数据
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"code": 400, "msg": "请求数据格式错误"})
        
        file_path = data.get('file_path')
        file_type = data.get('file_type', 'excel')
        
        if not file_path:
            return jsonify({"code": 400, "msg": "文件路径不能为空"})
        
        if not os.path.exists(file_path):
            return jsonify({"code": 400, "msg": "文件不存在"})
        
        result = import_controller.preview_file_data(file_path, file_type)
        return make_unicode_response(result)
    except Exception as e:
        return make_unicode_response({"code": 500, "msg": f"服务器内部错误: {str(e)}"})


@import_bp.route('/api/import_data', methods=['POST'])
def import_data():
    """
    导入数据到数据库
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"code": 400, "msg": "请求数据格式错误"})
        
        file_path = data.get('file_path')
        table_name = data.get('table_name')
        mapping_config = data.get('mapping_config', {})
        file_type = data.get('file_type', 'excel')
        
        if not file_path:
            return jsonify({"code": 400, "msg": "文件路径不能为空"})
        
        if not os.path.exists(file_path):
            return jsonify({"code": 400, "msg": "文件不存在"})
        
        if not table_name:
            return jsonify({"code": 400, "msg": "请选择目标表"})
        
        result = import_controller.import_data(file_path, table_name, mapping_config, file_type)
        return make_unicode_response(result)
    except Exception as e:
        return make_unicode_response({"code": 500, "msg": f"服务器内部错误: {str(e)}"})
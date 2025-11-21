# app/static/JsonData/sbgaData/json_api.py
from flask import Blueprint, render_template, request, redirect, url_for
from flask import Flask, request, jsonify, send_from_directory
import json
import os

#定义蓝图
jsonmanage = Blueprint('jsonmanage', __name__)
# 使用static目录下的JsonData/sbgaData作为JSON文件存储目录
CURRENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'JsonData', 'sbgaData')

# 服务静态文件
@jsonmanage.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(CURRENT_DIR, filename)

# 首页路由
@jsonmanage.route('/')
def index():
    return send_from_directory(CURRENT_DIR, 'jsonmanage.html')

# 查看页面路由
@jsonmanage.route('/view')
def view():
    return send_from_directory(CURRENT_DIR, 'view.html')

# 保存JSON数据的API端点
@jsonmanage.route('/api/save-json-data', methods=['POST'])
def save_json_data():
    try:
        # 获取请求数据
        request_data = request.get_json()
        filename = request_data.get('filename')
        json_data = request_data.get('data')
        
        if not filename or not json_data:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 定义文件路径
        file_path = os.path.join(CURRENT_DIR, filename)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        
        # 返回成功响应
        return jsonify({'success': True, 'message': '数据保存成功'})
    except Exception as e:
        print(f'保存数据时出错: {e}')
        return jsonify({'success': False, 'message': f'保存数据时出错: {str(e)}'}), 500

# 读取指定JSON文件内容的API端点
@jsonmanage.route('/api/read-json-file', methods=['GET'])
def read_json_file():
    try:
        # 从查询参数获取文件名
        filename = request.args.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'message': '缺少文件名参数'}), 400
        
        # 定义文件路径
        file_path = os.path.join(CURRENT_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '文件不存在'}), 404
            
        # 检查是否为JSON文件
        if not filename.endswith('.json'):
            return jsonify({'success': False, 'message': '只能读取JSON文件'}), 400
        
        # 读取并返回文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            json_content = json.load(f)
        
        return jsonify({'success': True, 'data': json_content, 'message': '文件读取成功'})
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
        return jsonify({'success': False, 'message': f'JSON文件格式错误: {str(e)}'}), 500
    except Exception as e:
        print(f'读取文件时出错: {e}')
        return jsonify({'success': False, 'message': f'读取文件时出错: {str(e)}'}), 500

# 创建新JSON文件的API端点
@jsonmanage.route('/api/create-json-file', methods=['POST'])
def create_json_file():
    try:
        # 获取请求数据
        request_data = request.get_json()
        
        # 打印请求数据以便调试
        print("收到的请求数据:", request_data)
        
        filename = request_data.get('filename')
        json_data = request_data.get('data')
        
        if not filename:
            return jsonify({'success': False, 'message': '缺少文件名参数'}), 400
        
        if not json_data:
            return jsonify({'success': False, 'message': '缺少数据参数'}), 400
            
        # 检查数据结构
        if not isinstance(json_data, dict):
            return jsonify({'success': False, 'message': '数据格式不正确'}), 400
            
        if 'name' not in json_data or 'objName' not in json_data or 'data' not in json_data:
            return jsonify({'success': False, 'message': '数据缺少必要字段(name, objName, data)'}), 400
        
        # 定义文件路径
        file_path = os.path.join(CURRENT_DIR, filename)
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            return jsonify({'success': False, 'message': '文件已存在'}), 400
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        
        # 返回成功响应
        return jsonify({'success': True, 'message': '文件创建成功'})
    except Exception as e:
        print(f'创建文件时出错: {e}')
        return jsonify({'success': False, 'message': f'创建文件时出错: {str(e)}'}), 500

# 获取文件列表的API端点
@jsonmanage.route('/api/json-files', methods=['GET'])
def get_json_files():
    try:
        # 获取目录下所有json文件
        files = [f for f in os.listdir(CURRENT_DIR) if f.endswith('.json')]
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        print(f'获取文件列表时出错: {e}')
        return jsonify({'success': False, 'message': f'获取文件列表时出错: {str(e)}'}), 500


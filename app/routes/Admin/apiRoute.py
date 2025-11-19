from flask import Blueprint, request, jsonify, send_from_directory
import json
import os
import requests
from urllib.parse import urlparse

# 定义蓝图
apimanager = Blueprint('apimanager', __name__)

# API数据文件路径
API_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'JsonData', 'sbgaData', 'api_endpoints.json')
FOLDERS_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'JsonData', 'sbgaData', 'api_folders.json')

# 确保数据文件存在
def ensure_data_file():
    os.makedirs(os.path.dirname(API_DATA_FILE), exist_ok=True)
    if not os.path.exists(API_DATA_FILE):
        with open(API_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists(FOLDERS_DATA_FILE):
        with open(FOLDERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# 获取所有API接口
@apimanager.route('/api/api-list', methods=['GET'])
def get_api_list():
    try:
        ensure_data_file()
        with open(API_DATA_FILE, 'r', encoding='utf-8') as f:
            apis = json.load(f)
        return jsonify({'success': True, 'data': apis})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 获取所有文件夹
@apimanager.route('/api/folder-list', methods=['GET'])
def get_folder_list():
    try:
        ensure_data_file()
        with open(FOLDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            folders = json.load(f)
        return jsonify({'success': True, 'data': folders})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 添加文件夹
@apimanager.route('/api/add-folder', methods=['POST'])
def add_folder():
    try:
        ensure_data_file()
        data = request.get_json()
        
        # 读取现有数据
        with open(FOLDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            folders = json.load(f)
        
        # 添加新文件夹
        data['id'] = max([folder.get('id', 0) for folder in folders]) + 1 if folders else 1
        
        # 如果没有提供parentId，则默认为null
        if 'parentId' not in data:
            data['parentId'] = None
            
        folders.append(data)
        
        # 保存数据
        with open(FOLDERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(folders, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '文件夹添加成功', 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 更新文件夹
@apimanager.route('/api/update-folder', methods=['POST'])
def update_folder():
    try:
        ensure_data_file()
        data = request.get_json()
        folder_id = data.get('id')
        
        # 读取现有数据
        with open(FOLDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            folders = json.load(f)
        
        # 查找并更新文件夹
        for i, folder in enumerate(folders):
            if folder.get('id') == folder_id:
                folders[i] = data
                break
        else:
            return jsonify({'success': False, 'message': '未找到指定文件夹'}), 404
        
        # 保存数据
        with open(FOLDERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(folders, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '文件夹更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 删除文件夹
@apimanager.route('/api/delete-api-by-folder', methods=['POST'])
def delete_api_by_folder():
    try:
        ensure_data_file()
        data = request.get_json()
        folder_id = data.get('folder_id')
        
        # 读取现有数据
        with open(API_DATA_FILE, 'r', encoding='utf-8') as f:
            apis = json.load(f)
        
        # 查找并删除属于该文件夹的API
        apis = [api for api in apis if api.get('folderId') != folder_id]
        
        # 保存数据
        with open(API_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': 'API删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@apimanager.route('/api/delete-folder', methods=['POST'])
def delete_folder():
    try:
        ensure_data_file()
        data = request.get_json()
        folder_id = data.get('id')
        
        # 读取现有数据
        with open(FOLDERS_DATA_FILE, 'r', encoding='utf-8') as f:
            folders = json.load(f)
        
        # 查找并删除文件夹及其子文件夹
        def get_all_child_folder_ids(parent_id):
            child_ids = []
            for folder in folders:
                if folder.get('parentId') == parent_id:
                    child_ids.append(folder.get('id'))
                    child_ids.extend(get_all_child_folder_ids(folder.get('id')))
            return child_ids
        
        # 获取所有要删除的文件夹ID（包括子文件夹）
        all_delete_ids = [folder_id]
        all_delete_ids.extend(get_all_child_folder_ids(folder_id))
        
        # 过滤掉要删除的文件夹
        folders = [folder for folder in folders if folder.get('id') not in all_delete_ids]
        
        # 保存数据
        with open(FOLDERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(folders, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '文件夹删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 添加API接口
@apimanager.route('/api/add-api', methods=['POST'])
def add_api():
    try:
        ensure_data_file()
        data = request.get_json()
        
        # 读取现有数据
        with open(API_DATA_FILE, 'r', encoding='utf-8') as f:
            apis = json.load(f)
        
        # 添加新API
        data['id'] = len(apis) + 1 if apis else 1
        apis.append(data)
        
        # 保存数据
        with open(API_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': 'API添加成功', 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 更新API接口
@apimanager.route('/api/update-api', methods=['POST'])
def update_api():
    try:
        ensure_data_file()
        data = request.get_json()
        api_id = data.get('id')
        
        # 读取现有数据
        with open(API_DATA_FILE, 'r', encoding='utf-8') as f:
            apis = json.load(f)
        
        # 查找并更新API
        for i, api in enumerate(apis):
            if api.get('id') == api_id:
                apis[i] = data
                break
        else:
            return jsonify({'success': False, 'message': '未找到指定API'}), 404
        
        # 保存数据
        with open(API_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': 'API更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 删除API接口
@apimanager.route('/api/delete-api', methods=['POST'])
def delete_api():
    try:
        ensure_data_file()
        data = request.get_json()
        api_id = data.get('id')
        
        # 读取现有数据
        with open(API_DATA_FILE, 'r', encoding='utf-8') as f:
            apis = json.load(f)
        
        # 查找并删除API
        apis = [api for api in apis if api.get('id') != api_id]
        
        # 保存数据
        with open(API_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': 'API删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 测试API接口
@apimanager.route('/api/test-api', methods=['POST'])
def test_api():
    try:
        data = request.get_json()
        url = data.get('url')
        method = data.get('method', 'GET').upper()
        headers = data.get('headers', {})
        params = data.get('params', {})
        body = data.get('body', '')
        
        # 验证URL
        if not url:
            return jsonify({'success': False, 'message': 'URL不能为空'}), 400
            
        # 解析URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return jsonify({'success': False, 'message': 'URL格式不正确'}), 400
        
        # 处理headers
        header_dict = {}
        if isinstance(headers, list):
            for header in headers:
                if 'key' in header and 'value' in header and header['key']:
                    header_dict[header['key']] = header['value']
        elif isinstance(headers, dict):
            header_dict = headers
            
        # 处理params
        param_dict = {}
        if isinstance(params, list):
            for param in params:
                if 'key' in param and 'value' in param and param['key']:
                    param_dict[param['key']] = param['value']
        elif isinstance(params, dict):
            param_dict = params
            
        # 发送请求
        if method == 'GET':
            response = requests.get(url, headers=header_dict, params=param_dict, timeout=30)
        elif method == 'POST':
            # 根据Content-Type判断body格式
            content_type = header_dict.get('Content-Type', '')
            if 'application/json' in content_type:
                # JSON格式
                response = requests.post(url, headers=header_dict, params=param_dict, 
                                       json=json.loads(body) if body else None, timeout=30)
            else:
                # 表单或其他格式
                response = requests.post(url, headers=header_dict, params=param_dict, 
                                       data=body, timeout=30)
        else:
            return jsonify({'success': False, 'message': f'不支持的请求方法: {method}'}), 400
            
        # 返回响应
        return jsonify({
            'success': True,
            'data': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text
            }
        })
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'message': f'JSON格式错误: {str(e)}'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'请求失败: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 主页路由
@apimanager.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), '../templates/Admin/SBGA/apimanager.html')
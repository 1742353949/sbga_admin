#认证相关路由
from flask import Blueprint, render_template, request, redirect, url_for
from app.helper.QLY_api import *
from config import qlyConfig

qly = Blueprint('qly', __name__)
_qlyClient = QLYClient(base_address=qlyConfig.BASE_ADDRESS, appid=qlyConfig.APPID, secret=qlyConfig.SECRET, rsa_private_key=qlyConfig.RSA_PRIVATE_KEY)

@qly.route('/qlyApi/v3/open/api/token', methods=['POST'])
def token():
    """获取Token"""
    data = request.get_json()
    operator_type = TokenOperatorType(data.get('operatorType', 1))
    action = data.get('action')
    target_type = data.get('targetType')
    target = data.get('target')
    
    try:
        result = _qlyClient.token_request(operator_type, action, target_type, target)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/device/list', methods=['POST'])
def device_list():
    """分页获取项目下设备列表"""
    data = request.get_json()
    page = data.get('page')
    page_size = data.get('pageSize')
    online_status = data.get('onlineStatus')
    
    try:
        result = _qlyClient.device_list(page, page_size, online_status)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data,
            "total": result.total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/node/tree', methods=['POST'])
def node_tree():
    """获取组织机构及子节点设备列表"""
    data = request.get_json()
    query_type = data.get('queryType')
    node_id = data.get('nodeId')
    device_id = data.get('deviceId')
    up = data.get('up')
    page = data.get('page')
    page_size = data.get('pageSize')
    query_region = data.get('queryRegion')
    
    try:
        result = _qlyClient.node_tree(query_type, node_id, device_id, up, page, page_size, query_region)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/device/info', methods=['POST'])
def device_info():
    """获取设备详细信息"""
    data = request.get_json()
    device_id = data.get('deviceId')
    
    try:
        result = _qlyClient.device_info(device_id)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data,
            "total": result.total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/store/device/detail/list', methods=['POST'])
def store_device_detail_list():
    """模糊搜索节点和设备详细信息"""
    data = request.get_json()
    store_id = data.get('storeId')
    query_type = data.get('queryType')
    query_keyword = data.get('queryKeyword')
    page = data.get('page')
    page_size = data.get('pageSize')
    
    try:
        result = _qlyClient.store_device_detail_list(store_id, query_type, query_keyword, page, page_size)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data,
            "total": result.total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/websdk/player', methods=['POST'])
def websdk_player():
    """获取摄像机视频播放WebSDK链接"""
    data = request.get_json()
    device_id = data.get('deviceId')
    end_time = data.get('endTime')
    
    try:
        result = _qlyClient.websdk_player(device_id, end_time)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyAPi/v3/open/api/websdk/live', methods=['POST'])
def websdk_live():
    """获取纯视频播放WebSDK链接（多屏播放）"""
    data = request.get_json()
    device_id = data.get('deviceId')
    end_time = data.get('endTime')
    
    try:
        result = _qlyClient.websdk_live(device_id, end_time)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qly.route('/qlyApi/v3/open/api/websdk/playback', methods=['POST'])
def websdk_playback():
    """获取指定时间段回看WebSDK链接"""
    data = request.get_json()
    device_id = data.get('deviceId')
    end_time = data.get('endTime')
    
    try:
        result = _qlyClient.websdk_playback(device_id, end_time)
        return jsonify({
            "resultCode": result.resultCode,
            "resultMsg": result.resultMsg,
            "data": result.data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500





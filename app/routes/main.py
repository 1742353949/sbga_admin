#主模块路由
from flask import Blueprint,make_response, render_template, request, redirect, url_for,jsonify
import websocket
import threading
import json
from config import config
from app.wsClient.wsClient import WebSocketClient
from app.helper.helper import *
from app.models.base_db import MySQLHelper  # 导入 MySQLHelper

main = Blueprint('main', __name__)

# ws_client = WebSocketClient(config["ws"].URL)
# ws_client.connect()

from app.controllers import MainController
from app.controllers.GridController import GridController

gridC = GridController()

@main.route('/')
# @cross_origin()
def helloworld():
    return f'helloworld'

@main.route("/ExportExecl")
def ExportExecl():
   return MainController.ExportExecl()

@main.route("/index")
def index():
   print(123)
   return MainController.index()

@main.route("/test1",methods=['POST','GET'])
def test1():
    header = request.headers
    type = request.form.get('obj')
    print(type)

    data = {
            "header":f"获取种植信息失败: {header}",
            "type":type,
            "projectName":"zzjd",
            "data":"son_raw_data",
            "msg":"chegngg"
            } 
    return echo_json(True,'success',data)

@main.route("/sqlQuery",methods=['POST','GET'])
def sqlQuery():
    content_type = request.content_type
    header = request.headers
    print(content_type)
    if content_type == "application/json":
        print("json格式")
        jsonData = request.get_json()
        type = jsonData.get("type")
        query = jsonData.get("query")
    elif content_type == "application/x-www-form-urlencoded":
        print("表单格式")
        type = request.form.get("type")
        query = request.form.get("query")
    else:
        print(f"不支持格式：{content_type}")
        type = request.form.get("type")
        query = request.form.get("query")
    print(type)
    print(query)
    print(header)
    result = MainController.sqlQuery(query)
    print(result)
    data = {
            "header":f"{header}",
            "type":type,
            "projectName":"zzjd",
            "data":result,
            "msg":"success"
            } 
    return echo_json(True,'success',data)

@main.route("/sqlUpdate",methods=['POST','GET'])
def sqlUpdate():
    header = request.headers
    type = request.form.get("type")
    query = request.form.get("query")
    print(type)
    print(query)
    result = MainController.sqlUpdate(query)
    print(result)
    data = {
            "header":f"{header}",
            "type":type,
            "projectName":"zzjd",
            "data":result,
            "msg":"success"
            } 
    return echo_json(True,'success',data)

@main.route("/rl_index")
def rl_index():
   return MainController.rl_index()
@main.route("/bs_mg")
def bs_mg():
   return MainController.bs_mg()

@main.route("/bs_mg/getPlantingInfo",methods=['POST','GET'])
def getPlantingInfo():
   username = request.form.get('name')
   print(username)
   return gridC.getPlantingInfo(username)
    # return gridC.test_database_connection()

@main.route("/bs_mg/getAllInfo",methods=['POST','GET'])
def getAllInfo():
   return gridC.getAllInfo()

@main.route('/greet/<name>')
def greet(name):
    return f'Hello, {name}!'

@main.route('/submit', methods=['POST','GET'])
def submit():
    username = request.form.get('username')
    return f'Hello, {username}!'

#响应
@main.route('/custom_response')
def custom_response():
    response = make_response('This is a custom response!')
    response.headers['token'] = '123'
    return response

@main.route('/hello/<name>')
def hello(name):
    return render_template('index.html', name=name)

@main.route('/test')
# @cross_origin()
def test():
    return f'hello,11'

@main.route('/deviceInfo',methods=['POST'])
def deviceInfo():
    # 确保 WebSocket 客户端已连接（此处为简化处理，未实现重连逻辑）
    # 从 POST 请求中获取数据（假设是 JSON 格式）
    try:
        raw_data = request.get_data()
        json_raw_data = json.loads(raw_data.decode('utf-8')) # 将字节串解码为字符串并解析为字典
        data = {
            "projectName":"zzjd",
            "type":"deviceInfo",
            "data":json_raw_data
            } 
    except json.JSONDecodeError:
        print('error：Invalid JSON data')
        return jsonify({'error': 'Invalid JSON data'}), 400
    if ws_client.ws :
        # 发送数据到 WebSocket 服务器
        data_str = json.dumps(data)
        ws_client.send_message(data_str)
        print(data)
        return data
    else:
        print('error: WebSocket connection not established')
        return jsonify({'error': 'WebSocket connection not established'}), 500
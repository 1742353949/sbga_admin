# -*- coding:utf-8 -*-

"""
@author:    tz_zs
"""

import websocket
from websocket import WebSocketApp
import json
from Post import *
from GetLocalInfo import EncodeDecode,IpConfigInfo

try:
    import thread
except ImportError:
    import _thread as thread
import time

import sys

import hashlib
import hmac
import base64
import time
import datetime

import uuid 
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
# sys.path.append("./getCameraList/")
# from getCameraList.getHikApiData import *


class websocketClient(object):
    """ websocket 监听 接收消息 并处理 ：
    parms :wsServerUrl //websocket 服务地址
    
    post请求 例 ： 
        Post:{
            "flag":"fly_start",
            "url":"http://112.116.71.17:8888/openApi/mission/executeMission",
            "data":{
                "mid":"123"
            }
        } 

       海康平台页面 http://172.0.250.3:9017/artemis-web/debug/1381003844548296704

    获取海康监控列表 例 ： 
        function:{
            "flag":"getCameraList",
            "data":{
                "host":"https://172.0.250.3",
                "port" : "1443",
                "appKey" : "25451111",
                "appSecret" : "BgdpJhHZ5OyebTLxdnpS",
                "api":"/api/resource/v1/camera/advance/cameraList"
            }
        }  

    启动http-server 例 ：
        function:{
            "flag":"http-server",
            "data":{
                "path":"D:/zzy/www/simple/",
                "port":""
            },
        }
        
    """
    

    def __init__(self,wsServerUrl):
        super(websocketClient, self).__init__()
        self.url = wsServerUrl
        self.ws = None
        self.IsClose = False
        self.conNum = 0

    def on_message(self, ws,message):
        try:
            msg = json.loads(message)
            print("####### on_message #######")
            # print("message：%s" % message)
            print(msg)
            projectName = msg.get("projectName")
            print(projectName)
            if(projectName == ProjectN):
                type = msg.get("type")
                print(type)
                if(type == "getHikApiData"):
                    data = msg.get("data")
                    # config = {
                    #     "host":'https://116.55.54.78',
                    #     "port":1443,
                    #     "appKey":'26721603',
                    #     "appSecret":'RPP50KBhCzt1AicadpPM'
                    #     }
                    # api='/api/resource/v1/cameras'
                    # body = {"pageNo":1,"pageSize":2}   
                    config = data.get("config")
                    api = data.get("api")
                    body = data.get("body") 
                    type = data.get("type") 
                    print("-------------------------------")
                    res = self.getApiData(config,api,body,type)
                    print("****************************")
                elif(type == "LocationWsClose"):
                    LocationId = msg.get("locationId") 
                    print(LocationId == _LocationId) 
                    print(LocationId)
                    print(_LocationId) 
                    if(LocationId == _LocationId):
                        self.ws.close()
                        self.IsClose = True
                        sys.exit(0)
        except Exception as e:
            print("出现错误：")
            print(e)
        
        
        if("Post:" in message):
            param_str = str(message.replace("Post:",""))
            msg = json.loads(param_str)
            url = str(msg.get("url"))
            data = msg.get("data")
            flag = msg.get("flag")
            print(data)
            print(url)
            # url = "http://112.116.71.17:8888/openapi/mission/executemission"
            print(url == "http://112.116.71.17:8888/openApi/mission/executeMission")
            res = Post("%s"%url,json.dumps(data))
            print(res)
            res = json.loads(res)
            msg = res.get("msg")
            res = "%s/%s" %(flag,msg)
            self.ws.send("%s" % res)
            print(msg)

        if("Function:" in message ):
            msg = json.loads(str(message.replace("Function:","")))
            data = msg.get("data")
            flag = msg.get("flag")

            """ 获取监控列表"""
            if(flag == "getCameraList"):
                host = data.get("host")
                port = data.get("port")
                appKey = data.get("appKey")
                appSecret = data.get("appSecret")
                api = data.get("api")
                cameralist = getCameraList(host,port,appKey,appSecret,api)
                with open('C:\Windows\Temp\cameraList.json', 'w') as f:
                    json.dump(cameralist,f)
                print(cameralist["msg"])




    def on_error(self, ws,error):
        print("####### on_error #######")
        print("error：%s" % error)
        print(self.IsClose)
        if(self.IsClose):
            return 0
        else:
            # thread.exit()
            self.start()
            # ws.close()

    def on_close(self,ws,a,b):
        print("####### on_close #######")
        print(~self.IsClose)
        print(self.IsClose)
        if(self.IsClose):
            return 0
        else:
            thread.exit()
            self.start()
        

    def on_ping(self, ws,message):
        print("####### on_ping #######")
        print("ping message：%s" % message)

    def on_pong(self, ws,message):
        print("####### on_pong #######")
        print("pong message：%s" % message)

    def on_open(self,ws):
        print("####### on_open #######")
        info = IpConfigInfo.getIpConfigInfo()
        # self.conNum+=1
        data = {
            "projectName":ProjectN,
            "type":"wsClient",
            "data":{
                "info":info
            }
        }
        self.ws.send(json.dumps(data))
        # threadName = "thread_%s"%self.conNum
        # thread.start_new_thread(self.run, (threadName))
        # print(thread)

    def run(self, name):
        while True:
            time.sleep(10)
            input_msg = input("%s等待中。。。"%name)
            if input_msg == "ws_Mz_close":
                self.ws.close()  # 关闭
                self.IsClose = True
                print("thread terminating...")
                break
            else:
                info = IpConfigInfo.getIpConfigInfo()
                self.ws.send(info)
                # self.ws.send(input_msg)
                # print(info)

    def start(self):
        """ 开始监听 """
        websocket.enableTrace(True)  # 开启运行状态追踪。debug 的时候最好打开他，便于追踪定位问题。

        self.ws = WebSocketApp(self.url,
                               on_open=self.on_open,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        # self.ws.on_open = self.on_open  # 也可以先创建对象再这样指定回调函数。run_forever 之前指定回调函数即可。

        self.ws.run_forever()

    def Signature(self,secret,methon,appKey,artemis,api):
        ## Timestamp
        t = time.time()
        nowTime = lambda:int(round(t * 1000))
        timestamp=nowTime()
        timestamp=str(timestamp)
        # uuid
        nonce= str(uuid.uuid1())
        #signature    
        secret=str(secret).encode('utf-8')
        message = str(methon+'\n*/*\napplication/json\nx-ca-key:'+appKey+'\nx-ca-nonce:'+nonce+'\nx-ca-timestamp:'+timestamp+'\n/'+artemis+api).encode('utf-8')
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())

        header_dict = dict()
        header_dict['Accept'] = '*/*'
        header_dict['Content-Type'] = 'application/json'
        header_dict['X-Ca-Key'] = appKey
        header_dict['X-Ca-Signature'] = signature
        header_dict['X-Ca-timestamp'] = timestamp
        header_dict['X-Ca-nonce'] = nonce
        header_dict['X-Ca-Signature-Headers'] = 'x-ca-key,x-ca-nonce,x-ca-timestamp'

        return header_dict
    
    def _getHeader(self,config = {"host":'https://116.55.54.78',"port":1443,"appKey":'26721603',"appSecret":'RPP50KBhCzt1AicadpPM'},api="/api/resource/v1/cameras"):
        # con = json.dumps(config)
        # print(config)
        # con = json.loads(con)
        con = config

        HOST = con.get("host")
        PORT = con.get("port")
        appKey=con.get("appKey")
        appSecret=con.get("appSecret")

        # print(PORT)
        # HOST = "https://116.55.54.78"
        # PORT = 1443
        # appKey='26721603'
        # appSecret='RPP50KBhCzt1AicadpPM'
        # print(HOST)
        # artemis api
        content='artemis' #上下文 默认artemis
        api = api # api 的url 
        methon = 'POST' # POST 或 GET 请求
        # Step3：组装POST请求URL
        # Setting Url
        url = HOST + ':' + str(PORT) +'/' +  content +  api 
        # print('https://116.55.54.78:1433/artemis/api/resource/v1/cameras'=='https://116.55.54.78:1443/artemis/api/resource/v1/cameras')
        print(url)

        # Step4：获取安全认证的Headers
        # Setting Headers
        header_dict=self.Signature(appSecret,methon,appKey,content,api)  # header 
        print(header_dict)
        return {"url": url, "header": header_dict}

    def getApiData(self,config,api='/api/resource/v1/cameras',body = {"pageNo":1,"pageSize":1000},type ='getApiData'):
        '''
        config = {
            "host":'https://116.55.54.78',
            "port":1443,
            "appKey":'26721603',
            "appSecret":'RPP50KBhCzt1AicadpPM'
            },
        api='/api/resource/v1/cameras',
        body = {"pageNo":1,"pageSize":1000}
        '''
        # api = '/api/resource/v1/cameras'
        
    
        try:
            retData = self._getHeader(config,api)
            url = retData["url"]
            header_dict = retData["header"]

            # Step5：组装传入的Json
            # Setting JSON Body
            # payload = {
            #     "pageNo": 1,
            #     "pageSize":1000,
            #     "cameraName": "全景"
            # }
            payload = {
                "pageNo": 1,
                "pageSize":1000
            }
            payload = body

            print("调用接口 getApiData")
            print(config)
            print(api)
            print(body)

            # Step6：发起POST请求
            # Make the requests allow_redirects=False 禁止重定向

            r = requests.post(url, headers=header_dict, json=payload,allow_redirects=False,verify=False)

            #Step7：解析请求响应
            # Check the response
            if r.status_code==302:
                result = r.headers['Location'] # 获取header返回的Location中的url
                # print('ResponseLocation:'+ result)
                return json.dumps({"code":302,"msg":"error","type":"RequestError"})

            else:
                result = json.loads(
                    r.content.decode('utf-8')
                )
                print(result)
                result['type'] = type
                self.ws.send(json.dumps(result))
                return result
            
            
        except Exception as e:
            print(e)
            data = json.dumps({
                    "code":-1,
                    "msg":"success",
                    "data":""
                })
            self.ws.send(json.dumps(data))
            return json.dumps({
                    "code":-1,
                    "msg":"success",
                    "data":""
                })

if __name__ == '__main__':
    # wsServerUrl = "ws://39.129.16.49:19001/websocket"
    # wsServerUrl = "ws://124.71.144.85:5001"
    # ProjectN = "zzjd"
    # print(sys.argv[0])
    wsServerUrl = sys.argv[1]
    ProjectN = sys.argv[2]
    _LocationId = sys.argv[3]
    print(wsServerUrl)
    print(ProjectN)
    print(_LocationId)
    websocketClient(wsServerUrl).start()
    



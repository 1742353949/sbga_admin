import json
import time
import hashlib
import base64
import requests
from enum import Enum
from typing import Optional, Dict, Any, TypeVar, Generic
from flask import Flask, jsonify, request

# 泛型类型定义
T = TypeVar('T')


class TokenOperatorType(Enum):
    """Token操作类型枚举"""
    AppToken = 1  # 应用token(拥有该应用全部权限)
    CustomToken = 2  # 自定义token(拥有该应用部分权限)


class RespBase:
    """响应基类"""
    def __init__(self, data: Dict[str, Any]):
        self.resultCode = data.get("resultCode")
        self.resultMsg = data.get("resultMsg")

class RespObject(RespBase, Generic[T]):
    """对象类型响应"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.data = data.get("data")  # 具体数据对象


class RespArray(RespBase, Generic[T]):
    """数组类型响应"""
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.data = data.get("data", [])  # 数据数组
        self.total = data.get("total", 0)  # 总条数


class QLYClient:
    """QLY客户端类"""
    def __init__(self, base_address: str, appid: str, secret: str, rsa_private_key: str, proxies: Optional[Dict[str, str]] = None):
        self.base_address = base_address
        self.appid = appid
        self.secret = secret
        self.rsa_private_key = rsa_private_key
        self.token = "Token"  # 初始token
        self.session = requests.Session()
        # 添加代理设置，如果proxies为None或空字典，则不使用代理
        if proxies:
            # 验证代理配置是否有效
            try:
                self.session.proxies = proxies
            except Exception as e:
                print(f"警告: 代理配置无效，将不使用代理: {str(e)}")
                self.session.proxies = {}

    def get_md5(self, data: str) -> str:
        """计算MD5哈希值"""
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode('utf-8'))
        return md5_hash.hexdigest()

    def _sign_request(self, body: str, token: Optional[str] = None) -> Dict[str, str]:
        """生成请求签名头"""
        # 构建签名对象
        signature_obj = {
            "appid": self.appid,
            "md5": self.get_md5(body),
            "timestamp": str(int(time.time() * 1000)),
            # "timestamp": '1761740484482',
            "token": "Token",
            "version": "1.0.0"
        }
        print(f"时间戳：{signature_obj['timestamp']}")

        # 如有token则添加
        if token:
            signature_obj["token"] = token

        # 转换为无格式JSON字符串
        signature_str = json.dumps(signature_obj, separators=(',', ':'))

        # 使用RSA私钥签名(SHA1withRSA)
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend

        # 处理私钥格式
        private_key_pem = f"-----BEGIN PRIVATE KEY-----\n{self.rsa_private_key}\n-----END PRIVATE KEY-----"
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        # 签名并转换为Base64
        signature_bytes = private_key.sign(
            signature_str.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        signature = base64.b64encode(signature_bytes).decode('utf-8')

        # 构建请求头
        headers = {
            "appid": self.appid,
            "md5": signature_obj["md5"],
            "timestamp": signature_obj["timestamp"],
            "token":"Token",
            "version": "1.0.0",
            "signature": signature,
            "Content-Type": "application/json"
        }
        if token:
            headers["token"] = token
        

        return headers

    def post(self, api: str, body: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.base_address}{api}"
        body_str = json.dumps(body, separators=(',', ':'))
        headers = self._sign_request(body_str, token)
        
        try:
            response = self.session.post(
                url,
                data=body_str,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ProxyError as e:
            # 检查是否配置了代理
            if self.session.proxies:
                raise Exception(f"代理连接失败，请检查代理设置: {str(e)}")
            else:
                raise Exception(f"网络连接失败，请检查网络设置: {str(e)}")
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")

    def token_request(self, operator_type: TokenOperatorType, 
                          action: Optional[str] = None,
                          target_type: Optional[str] = None,
                          target: Optional[str] = None) -> RespObject[Dict[str, Any]]:
        """获取Token"""
        body = {
            "sig": self.get_md5(self.appid + self.secret),
            "operatorType": operator_type.value
        }

        if action:
            body["action"] = action
        if target_type:
            body["targetType"] = target_type
        if target:
            body["target"] = target

        result = self.post("/v3/open/api/token", body)
        return RespObject(result)


    def token_post(self, api: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """带Token的POST请求（自动刷新Token）"""
        result = self.post(api, body, self.token)
        
        # 处理Token过期情况
        if result.get("resultCode") in ["11503", "11504"]:
            # 重新获取AppToken
            token_resp = self.token_request(TokenOperatorType.AppToken)
            if token_resp.resultCode == "000000":
                self.token = token_resp.data.get("token")
                # 重试请求
                return self.post(api, body, self.token)
            else:
                raise Exception(f"Token刷新失败: {token_resp.resultMsg}")
        
        return result

    def device_list(self, 
                        page: Optional[int] = None, 
                        page_size: Optional[int] = None, 
                        online_status: Optional[int] = None) -> RespArray[Dict[str, Any]]:
        """分页获取项目下设备列表"""
        body = {}
        if page is not None:
            body["page"] = page
        if page_size is not None:
            body["pageSize"] = page_size
        if online_status is not None:
            body["onlineStatus"] = online_status

        result = self.token_post("/v3/open/api/device/list", body)
        return RespArray(result)

    def node_tree(self, 
                      query_type: int, 
                      node_id: Optional[str] = None, 
                      device_id: Optional[str] = None, 
                      up: Optional[int] = None, 
                      page: Optional[int] = None, 
                      page_size: Optional[int] = None, 
                      query_region: Optional[str] = None) -> RespObject[Dict[str, Any]]:
        """获取组织机构及子节点设备列表"""
        body = {"queryType": query_type}
        
        if node_id:
            body["nodeId"] = node_id
        if device_id:
            body["deviceId"] = device_id
        if up is not None:
            body["up"] = up
        if page is not None:
            body["page"] = page
        if page_size is not None:
            body["pageSize"] = page_size
        if query_region:
            body["queryRegion"] = query_region

        result = self.token_post("/v3/open/api/node/tree", body)
        return RespObject(result)

    def device_info(self, device_id: str) -> RespArray[Dict[str, Any]]:
        """获取设备详细信息"""
        body = {"deviceId": device_id}
        result = self.token_post("/v3/open/api/device/info", body)
        return RespArray(result)

    def store_device_detail_list(self, 
                                     store_id: str, 
                                     query_type: int, 
                                     query_keyword: Optional[str] = None, 
                                     page: Optional[int] = None, 
                                     page_size: Optional[int] = None) -> RespArray[Dict[str, Any]]:
        """模糊搜索节点和设备详细信息"""
        body = {
            "storeId": store_id,
            "queryType": query_type
        }
        
        if query_keyword:
            body["queryKeyword"] = query_keyword
        if page is not None:
            body["page"] = page
        if page_size is not None:
            body["pageSize"] = page_size

        result = self.token_post("/v3/open/api/store/device/detail/list", body)
        return RespArray(result)

    def websdk_player(self, device_id: str, end_time: Optional[int] = None) -> RespObject[Dict[str, Any]]:
        """获取摄像机视频播放WebSDK链接"""
        body = {"deviceId": device_id}
        if end_time is not None:
            body["endTime"] = end_time

        result = self.token_post("/v3/open/api/websdk/player", body)
        return RespObject(result)

    def websdk_live(self, device_id: str, end_time: Optional[int] = None) -> RespObject[Dict[str, Any]]:
        """获取纯视频播放WebSDK链接（多屏播放）"""
        body = {"deviceId": device_id}
        if end_time is not None:
            body["endTime"] = end_time

        result = self.token_post("/v3/open/api/websdk/live", body)
        return RespObject(result)

    def websdk_playback(self, device_id: str, end_time: Optional[int] = None) -> RespObject[Dict[str, Any]]:
        """获取指定时间段回看WebSDK链接"""
        body = {"deviceId": device_id}
        if end_time is not None:
            body["endTime"] = end_time

        result = self.token_post("/v3/open/api/websdk/playback", body)
        return RespObject(result)


if __name__ == "__main__":
    # 创建QLY客户端实例
    _qlyClient = QLYClient(
        base_address="https://open.andmu.cn",
        appid="6c087dbb5a074c13a011befc6b835fe5",
        secret="qWSk4oQ5f8UHKXQO",
        rsa_private_key="MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAIFnG+jvrnNbFzXArfG/dFH38n0p5pg9P3chIFn8MEvXHNDcdAa86SG35kghMwM37FKRq5NoTs0j81RIr7pqilF4pLqK6ZhDTjCXp5UK3zT4vnNecUJETSE/FgKtMeHsf9hv8zFmbqL0R/Ycgj+ZJ/Pr8Kuw/zV014bpOMLAi4hFAgMBAAECgYBaf8wLKqUs1AX1d92u9qDZOrkCRC2bRyp9nFNN24vDXpwujh8vHytEg6Kvy1gr5g6G6I3AN/D0kzH4PiV4EE7PERAIV2LfXMsgX7D949xz7M4OTcCXUDQCHde4EpIxvgZzRONYgDWD/gguc5b3dKcy9qAzv80To2gL+VFDvi24gQJBALq+/KW6Kk4O2wpYHcrNnFAEJKh7WI7dKUb5cfSr0y49rM9cY89BXrPcwqlB/spfkdTKQtsaNY1QPszjCIo13BECQQCxZCc9F57X0iftFK0wZO5o7oZGcCMk77crI/X4h9IhJurw8q+WoR4HIlqVJXLdsSlMoQo1RuRayjs+21LXXSz1AkBQmDR5Ycr4PTkTUcwpxmr7rY4UmIczwQcbdnRT4AQYJM38ACejPtccUN5CJhVMScqqR1BrNvh9sHAqBKGe5HfBAkBrlPP/Jw4ckcXJENsgGHZGiTJCEcweoIsTzNFmEukrVfDyhBxdXAVcCkepYHbTYJhNcvU/7mibbz6TFmydVFLpAkBdXdw4n+a5ZVPVsGmyT1tVxxCryJlwl2FAePuEtF9d847Q1Nz62A9u38/Xxx9SxWUIIE5AIGBewdtdDJaLf8Rh",
        # 如果需要使用代理，请取消下面的注释并配置正确的代理地址
        # proxies={
        #     "http": "http://proxy.example.com:8080",
        #     "https": "http://proxy.example.com:8080"
        # }
    )
    result = _qlyClient.node_tree(query_type=0,node_id='1274322021279854592')
    print(result)
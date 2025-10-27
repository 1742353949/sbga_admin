import json
import urllib.request
import urllib.parse
def http_get(url):
    re_url = url
    try:
        reqs = urllib.request.Request(re_url)
        response = urllib.request.urlopen(reqs)
        
        content = response.read().decode('utf-8')
        content = json.loads(content)
        return content
    except Exception as e:
         print(e)
         return []
         
def http_post(url='', data={},headers={}):
    """
    发送POST请求
    :param url: 请求的URL
    :param data: 请求参数字典
    :return: 响应结果
    """
    # 将参数编码为URL编码格式
    data = urllib.parse.urlencode(data).encode('utf-8')
    
    # 创建请求对象
    req = urllib.request.Request(url=url, data=data,headers=headers)
    
    # 发送POST请求并获取响应
    with urllib.request.urlopen(req) as response:
        # 读取响应内容并解码
        response_data = response.read().decode('utf-8')
        
        # 将响应内容解析为JSON格式
        return json.loads(response_data)


     
if __name__ == '__main__':     
    pass
from flask import jsonify,make_response,request
import os
import platform
import secrets
import pytz,datetime
from datetime import datetime as dt  # 使用别名避免冲突

def gen_md5(_pwd):
    import hashlib
    '''md5密码生成
        如需要：可使用_pwd.update(b'#$%')对密码进行附加加密
    '''
    _pwd = hashlib.md5(_pwd.encode('utf-8'))
    _pwd.update(b'!@#')
    return _pwd.hexdigest()

def base64_encode(_str):
    import base64
    try:
        data_bytes = _str.encode('utf-8')
        return base64.b64encode(data_bytes)
    except Exception as e:
        print(e)
        return False
    
def base64_decode(_str):
    import base64
    try:
        decoded_bytes = base64.b64decode(_str)
        # 将字节解码回原始字符串
        decoded_data = decoded_bytes.decode('utf-8')

        # 输出解码后的字符串
        return decoded_data
    except Exception as e:
        print(e)
        return False
    
def echo_json(status, message, data = None, other = None,code=200):
    '''输出json结果
        Args:
            status: 状态码0=success, 非0为失败
            msg: 输出消息
            data: 返回的数据

        Returns:

            {'status': status, 'msg': message, 'data': data, 'other': other}
    '''
    response = make_response(jsonify({'status': status, 'msg': message, 'data': data, 'other': other}),code)
    response.autocorrect_headers = False  # 防止Flask修改非标准状态码
    return response

def get_page_param():
    '''获取分页数据
        如无分分页数据，则返回默认值[pageindex=0,pagesize=50] 

        Retures:
            [pageindex, pagesize]
    '''
    pageindex = 0
    pagesize = 20
    try:
            #print(request.values)
        if request.values.get("page") is not None:
            pageindex = int(request.values.get("page"))
        elif request.headers['page'] is not None:
            pageindex = int(request.headers["page"])

        if request.values.get("pagesize") is not None:
            pagesize = int(request.values.get("pagesize"))
        elif request.headers['pagesize'] is not None:
            pagesize = int(request.headers["pagesize"])

        return [pageindex, pagesize]
    except Exception as e:
        return [pageindex, pagesize]

def get_param_by_int(_name):
    '''获取页面数值类型数据
        Retures:
            页面参数
    '''

    value = 0
    try:
        if request.values.get(_name) is not None:
            value = int(request.values.get(_name))
       
        return value
    except Exception as e:
        return 0

def get_param_by_str(_name):
    '''获取页面类型数据
        Retures:
            页面参数
    '''
    value = ''
    try:
        if request.values.get(_name) is not None:
            value = request.values.get(_name)
       
        return value
    except Exception as e:
        return ''
    
def get_param_by_json(_name):
    '''获取页面类型数据
        Retures:
            页面参数
    '''
    value = ''
    try:
        json_data = request.get_json()
        value = json_data[_name]
        
        return value
    except Exception as e:
        return ''

def get_user_token():
    """获取用户token
        Retures:
            token
    """
    token = request.headers.get('Authorization','')
    return token
def get_header_token_by_bearer():
    """获取header中的Authorization验证，基于Bearer 认证
        Retures:
            token
    """
    from flask import abort,request
    token = request.headers.get('Authorization', '').replace('Bearer ', '')  # 提取并清理token
    # 验证token
    #if token != "kmlskj":
    #    abort(401, description="Unauthorized Access")
def Is_Chinese(word):
    '''判断是否为中文，只要带中文均返回True
    '''
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def find_file(search_path, include_str=None, filter_strs=None):
    """
    查找指定目录下所有的文件（不包含以__开头和结尾的文件）或指定格式的文件，若不同目录存在相同文件名，只返回第1个文件的路径
    :param search_path: 查找的目录路径
    :param include_str: 获取包含字符串的名称
    :param filter_strs: 过滤包含字符串的名称
    """
    if filter_strs is None:
        filter_strs = []

    files = []
    # 获取路径下所有文件
    names = os.listdir(search_path)
    for name in names:
        path = os.path.abspath(os.path.join(search_path, name))
        if os.path.isfile(path):
            # 如果不包含指定字符串则
            if include_str is not None and include_str not in name:
                continue

            # 如果未break，说明不包含filter_strs中的字符
            for filter_str in filter_strs:
                if filter_str in name:
                    break
            else:
                files.append(path)
        else:
            files += find_file(path, include_str=include_str, filter_strs=filter_strs)
    return files

def create_dir(_path):
    '''创建目录,注不递归创建目录
    '''
    import stat
    if not os.path.exists(_path):
        os.mkdir(_path)
        os.chmod(_path,stat.S_IRWXU | stat.S_IRGRP |stat.S_IRWXO)

def delete_file(_fname):
    ''' 删除指定文件
        Args:
            fname: 文件相对路径
    '''
    full_path = os.path.abspath('') + _fname
    if os.path.isfile(full_path) and os.path.exists(full_path):
        os.remove(full_path)

def diff_seconds(start_time, end_time):
    ''' 计算两个字符串时间相差多少秒
        Args:
            start_time: 开始时间如：2023-08-07 12:23:55
            end_time: 结束时间如：2023-08-07 13:19:45 
        Return: 
            int: 查差多少秒
        @date:   2023/08/07 23:42:46
        @author: snz
    '''
    
    from datetime import datetime
    _s = datetime.strptime(str(start_time),"%Y-%m-%d %H:%M:%S")
    _e = datetime.strptime(str(end_time),"%Y-%m-%d %H:%M:%S")
    return (_e - _s).seconds

def calculate_time_difference(send_time):
    """计算与当前时间相差的秒数
    :"""
    from datetime import datetime
    # 获取当前时间
    current_time = dt.now()
    
    # 假设 send_time 是从数据库中读取出来的 datetime 对象
    # 如果是从字符串读取，需要先转换为 datetime 对象
    # send_time = datetime.strptime(send_time_str, '%Y-%m-%d %H:%M:%S')
    
    # 计算时间差
    time_difference = current_time - send_time
    
    # 将时间差转换为秒
    time_difference_in_seconds = time_difference.total_seconds()
    
    return time_difference_in_seconds

# 示例使用
# 假设 send_time 是从数据库中读取出来的 datetime 对象
send_time = dt(2023, 10, 1, 12, 0, 0)  # 示例时间
seconds_difference = calculate_time_difference(send_time)
print(f"时间差为 {seconds_difference} 秒")
def generate_float(min_value, max_value):
    """
    生成指定范围内的浮点数，并保留两位小数点。
    
    :param min_value: 浮点数的最小值
    :param max_value: 浮点数的最大值
    :return: 保留两位小数的浮点数
    """
    import random
    # 生成随机浮点数
    float_number = random.uniform(min_value, max_value)
    
    # 保留两位小数
    formatted_number = round(float_number, 2)
    
    return formatted_number

def pdf2img(pdf_path, img_dir):
    '''
    """
        pdf转换img
        pip install PyMuPDF==1.18.17 -i https://pypi.tuna.tsinghua.edu.cn/simple
        Args:
            pdf_path: pdf文件路径
            img_dir: 图片保存路径
        Returns:
            img_list: 图片路径列表

        Remarks:
        base_path = os.path.join(os.path.abspath(''), 'static/upload')
        pdf2img(base_path+"/1.pdf",base_path)
    """
    _sp = '/'
    if platform.system().lower() == 'windows':
        _sp = '\\'

    import fitz
    if img_dir != "" and img_dir[-1] != _sp:
        img_dir += _sp
        

    _base_path = os.path.abspath('')
    ret_img_list = []
    doc = fitz.open(pdf_path)  # 打开pdf

    for page in doc:  # 遍历pdf的每一页
        zoom_x = 2.0  # 设置每页的水平缩放因子
        zoom_y = 2.0  # 设置每页的垂直缩放因子
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        _img_path = r"{}page-{}.png".format(img_dir, page.number)
        pix.save(_img_path)     # 保存

        _img_path = _img_path.replace(_base_path,'')
        ret_img_list.append(_img_path)

    return ret_img_list
    '''
    pass

def pinyin(cn_str):
    '''
    """文字转拼音
        Args:
            cn_str: 中文字符串
        Returns:
            str: 拼音字符串
    """
    from pypinyin import lazy_pinyin, Style
    try:
        return "_".join(lazy_pinyin(cn_str))
    except:
        return cn_str
    '''
    pass

def generate_auth_token():
    return secrets.token_hex(16)  # 生成随机 Token

def get_current_time():
        '''
        获取当前时间
        '''
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.datetime.now(china_tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S")

def get_real_ip():
    """
    获取客户端的真实IP地址。

    此函数会尝试从请求头中获取 'X-Forwarded-For' 字段，如果存在则取第一个IP地址作为真实IP；
    如果不存在，则使用请求的远程地址作为真实IP。

    Returns:
        str: 客户端的真实IP地址。
    """
    # 尝试从请求头中获取 'X-Forwarded-For' 字段
    real_ip = request.headers.get('X-Forwarded-For')
    if real_ip:
        # 如果 'X-Forwarded-For' 字段存在，取第一个IP地址作为真实IP
        real_ip = real_ip.split(',')[0]
    else:
        # 如果 'X-Forwarded-For' 字段不存在，使用请求的远程地址作为真实IP
        real_ip = request.remote_addr

    return real_ip
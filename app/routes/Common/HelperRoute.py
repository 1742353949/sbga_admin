from flask import Blueprint, render_template, request, redirect, url_for
import math
from app.helper.helper import *
from config import qlyConfig

help = Blueprint('help', __name__,url_prefix='/help')

@help.route('', methods=['POST','GET'])
def index():
    return f"Help index"


#
# 坐标转换接口，支持BD-09、GCJ-02、WGS-84和CGCS2000坐标系之间的相互转换
# 支持GET和POST两种请求方式
# GET请求参数：
#   source_type: 源坐标系类型 (bd09, gcj02, wgs84, cgcs2000)
#   target_type: 目标坐标系类型 (bd09, gcj02, wgs84, cgcs2000)
#   lat: 纬度
#   lng: 经度
# POST请求参数：
#   source_type: 源坐标系类型 (bd09, gcj02, wgs84, cgcs2000)
#   target_type: 目标坐标系类型 (bd09, gcj02, wgs84, cgcs2000)
#   lat: 纬度
#   lng: 经度
# 返回值：
#   成功时返回转换后的坐标信息，包括lat、lng和lnglat字段
#   失败时返回错误信息和状态码
@help.route('/convert', methods=['GET', 'POST'])
def convert_coordinates():
    if request.method == 'GET':
        source_type = request.args.get('source_type')
        target_type = request.args.get('target_type')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
    elif request.method == 'POST':
        data = request.get_json()
        source_type = data.get('source_type')
        target_type = data.get('target_type')
        lat = data.get('lat')
        lng = data.get('lng')
    
    if not source_type or not target_type or not lat or not lng:
        return {"error": "Missing required parameters"}, 400
    
    # BD-09 to GCJ-02 conversion
    # 百度坐标系转火星坐标系
    # 参数：bd_lon - 百度经度，bd_lat - 百度纬度
    # 返回：gcj_lon - 火星经度，gcj_lat - 火星纬度
    def bd09_to_gcj02(bd_lon, bd_lat):
        x = float(bd_lon) - 0.0065
        y = float(bd_lat) - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * math.pi / 180)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * math.pi / 180)
        gcj_lon = z * math.cos(theta)
        gcj_lat = z * math.sin(theta)
        return gcj_lon, gcj_lat

    # GCJ-02 to BD-09 conversion
    # 火星坐标系转百度坐标系
    # 参数：gcj_lon - 火星经度，gcj_lat - 火星纬度
    # 返回：bd_lon - 百度经度，bd_lat - 百度纬度
    def gcj02_to_bd09(gcj_lon, gcj_lat):
        x = float(gcj_lon)
        y = float(gcj_lat)
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * math.pi / 180)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * math.pi / 180)
        bd_lon = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return bd_lon, bd_lat

    # 更精确的GCJ-02到WGS-84转换算法
    # 火星坐标系转WGS-84坐标系（精确算法）
    # 参数：gcj_lng - 火星经度，gcj_lat - 火星纬度
    # 返回：wgs_lng - WGS-84经度，wgs_lat - WGS-84纬度
    def gcj02_to_wgs84(gcj_lng, gcj_lat):
        # 转换参数
        a = 6378245.0  # 长半轴
        ee = 0.00669342162296594323  # 偏心率平方
        
        def transform_lat(x, y):
            ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
            return ret

        def transform_lng(x, y):
            ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
            return ret

        # 经纬度转换为弧度
        d_lat = transform_lat(float(gcj_lng) - 105.0, float(gcj_lat) - 35.0)
        d_lng = transform_lng(float(gcj_lng) - 105.0, float(gcj_lat) - 35.0)
        
        # 转换精度
        rad_lat = float(gcj_lat) / 180.0 * math.pi
        magic = math.sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = math.sqrt(magic)
        
        d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * math.pi)
        d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * math.pi)
        
        # 计算WGS-84坐标
        wgs_lat = float(gcj_lat) - d_lat
        wgs_lng = float(gcj_lng) - d_lng
        
        return wgs_lng, wgs_lat

    # WGS-84 to GCJ-02 conversion (approximate)
    # WGS-84坐标系转火星坐标系（近似算法）
    # 参数：wgs_lon - WGS-84经度，wgs_lat - WGS-84纬度
    # 返回：gcj_lon - 火星经度，gcj_lat - 火星纬度
    def wgs84_to_gcj02(wgs_lon, wgs_lat):
        gcj_lon = wgs_lon + 0.0065
        gcj_lat = wgs_lat + 0.006
        return gcj_lon, gcj_lat

    # WGS-84 to BD-09 conversion
    # WGS-84坐标系转百度坐标系
    # 参数：wgs_lon - WGS-84经度，wgs_lat - WGS-84纬度
    # 返回：bd_lng - 百度经度，bd_lat - 百度纬度
    def wgs84_to_bd09(wgs_lon, wgs_lat):
        gcj_lng, gcj_lat = wgs84_to_gcj02(wgs_lon, wgs_lat)
        bd_lng, bd_lat = gcj02_to_bd09(gcj_lng, gcj_lat)
        return bd_lng, bd_lat

    # BD-09 to WGS-84 conversion
    # 百度坐标系转WGS-84坐标系
    # 参数：bd_lon - 百度经度，bd_lat - 百度纬度
    # 返回：wgs_lng - WGS-84经度，wgs_lat - WGS-84纬度
    def bd09_to_wgs84(bd_lon, bd_lat):
        gcj_lng, gcj_lat = bd09_to_gcj02(bd_lon, bd_lat)
        wgs_lng, wgs_lat = gcj02_to_wgs84(gcj_lng, gcj_lat)
        return wgs_lng, wgs_lat

    # CGCS2000与WGS84之间的转换函数
    # CGCS2000和WGS84非常接近，对于大多数应用可以认为是相同的坐标系
    # 如果需要更高精度，可以在此处添加更复杂的转换逻辑
    # CGCS2000转WGS-84坐标系
    # 参数：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    # 返回：wgs_lon - WGS-84经度，wgs_lat - WGS-84纬度
    def cgcs2000_to_wgs84(cgcs_lon, cgcs_lat):
        # 在大多数情况下，CGCS2000和WGS84可以互换使用
        # 这里直接返回原始值，如需高精度转换可添加具体算法
        return float(cgcs_lon), float(cgcs_lat)
    
    # WGS-84转CGCS2000坐标系
    # 参数：wgs_lon - WGS-84经度，wgs_lat - WGS-84纬度
    # 返回：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    def wgs84_to_cgcs2000(wgs_lon, wgs_lat):
        # 在大多数情况下，CGCS2000和WGS84可以互换使用
        # 这里直接返回原始值，如需高精度转换可添加具体算法
        return float(wgs_lon), float(wgs_lat)
    
    # CGCS2000与其他坐标系的转换函数
    # CGCS2000转火星坐标系
    # 参数：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    # 返回：gcj_lon - 火星经度，gcj_lat - 火星纬度
    def cgcs2000_to_gcj02(cgcs_lon, cgcs_lat):
        wgs_lon, wgs_lat = cgcs2000_to_wgs84(cgcs_lon, cgcs_lat)
        return wgs84_to_gcj02(wgs_lon, wgs_lat)
    
    # 火星坐标系转CGCS2000坐标系
    # 参数：gcj_lon - 火星经度，gcj_lat - 火星纬度
    # 返回：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    def gcj02_to_cgcs2000(gcj_lon, gcj_lat):
        wgs_lon, wgs_lat = gcj02_to_wgs84(gcj_lon, gcj_lat)
        return wgs84_to_cgcs2000(wgs_lon, wgs_lat)
    
    # CGCS2000转百度坐标系
    # 参数：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    # 返回：bd_lng - 百度经度，bd_lat - 百度纬度
    def cgcs2000_to_bd09(cgcs_lon, cgcs_lat):
        wgs_lon, wgs_lat = cgcs2000_to_wgs84(cgcs_lon, cgcs_lat)
        return wgs84_to_bd09(wgs_lon, wgs_lat)
    
    # 百度坐标系转CGCS2000坐标系
    # 参数：bd_lon - 百度经度，bd_lat - 百度纬度
    # 返回：cgcs_lon - CGCS2000经度，cgcs_lat - CGCS2000纬度
    def bd09_to_cgcs2000(bd_lon, bd_lat):
        wgs_lon, wgs_lat = bd09_to_wgs84(bd_lon, bd_lat)
        return wgs84_to_cgcs2000(wgs_lon, wgs_lat)

    # 根据源类型和目标类型执行相应转换
    if source_type == target_type:
        result = {"lat": lat, "lng": lng, "lnglat": f"{lng},{lat}"}
    elif source_type == "bd09" and target_type == "gcj02":
        result_lng, result_lat = bd09_to_gcj02(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "gcj02" and target_type == "bd09":
        result_lng, result_lat = gcj02_to_bd09(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "gcj02" and target_type == "wgs84":
        result_lng, result_lat = gcj02_to_wgs84(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "wgs84" and target_type == "gcj02":
        result_lng, result_lat = wgs84_to_gcj02(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "wgs84" and target_type == "bd09":
        result_lng, result_lat = wgs84_to_bd09(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "bd09" and target_type == "wgs84":
        result_lng, result_lat = bd09_to_wgs84(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    # 新增CGCS2000相关的转换分支
    elif source_type == "cgcs2000" and target_type == "wgs84":
        result_lng, result_lat = cgcs2000_to_wgs84(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "wgs84" and target_type == "cgcs2000":
        result_lng, result_lat = wgs84_to_cgcs2000(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "cgcs2000" and target_type == "gcj02":
        result_lng, result_lat = cgcs2000_to_gcj02(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "gcj02" and target_type == "cgcs2000":
        result_lng, result_lat = gcj02_to_cgcs2000(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "cgcs2000" and target_type == "bd09":
        result_lng, result_lat = cgcs2000_to_bd09(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    elif source_type == "bd09" and target_type == "cgcs2000":
        result_lng, result_lat = bd09_to_cgcs2000(lng, lat)
        result = {"lat": result_lat, "lng": result_lng, "lnglat": f"{result_lng},{result_lat}"}
    else:
        return {"error": "Unsupported conversion type"}, 400

    return echo_json(0, "success", result)
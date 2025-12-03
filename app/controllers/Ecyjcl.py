# 导入数据库操作基础类，提供数据库连接和CRUD核心能力
from app.models.base_db import MySQLHelper
# 导入Flask蓝图、JSON响应处理、请求对象，用于构建API接口
from flask import Blueprint, jsonify, request
# 导入日志模块，用于调试和运行状态记录
import logging
# 导入日期时间处理模块，用于时间格式转换和时间段计算
from datetime import datetime, timedelta
# 导入JSON模块，用于处理codes/names字段的序列化与反序列化
import json
from app.helper.helper import *

# 创建Flask蓝图，命名为'ecyj'，URL前缀为'/ecyj'，统一管理预警相关接口路由
ecyj = Blueprint('ecyj', __name__, url_prefix='/ecyj')


# 1.创建数据库操作类，继承自MySQLHelper，封装预警相关数据处理逻辑
class ecyj_tb(MySQLHelper):
    def __init__(self):
        """初始化预警数据处理类，调用父类构造方法初始化数据库连接"""
        super().__init__()

    #获取时间配置
    def get_early_warning_config(self):
        """
        获取预警配置参数（原有注释保留）
        从wd_ecyj_yddr表查询预警规则配置，包含次数阈值、人数阈值、时间阈值
        :return: 配置字典 {times: 次数阈值, people_num: 人数阈值, ex_time: 时间阈值}，查询无结果返回None
        """
        sql = "SELECT times, people_num, ex_time FROM wd_ecyj_yddr "
        result = self.execute_query(sql)        
        return result
    # 获取hist数据
    def get_hist_data(self):
        """
         查询有效hist数据：name非空、未处理（processed=0），按捕获时间降序取前100条（控制数据量）
        """
        hist_sql="""
        SELECT id, objtype, channelId, channelName, name, cardNo, capTimestr 
        FROM hist 
        WHERE name IS NOT NULL AND name != '' AND processed = 0 
        ORDER BY capTime DESC
        LIMIT 100
        """
        hist_records=self.execute_query(hist_sql)
       #print('=== 待处理hist记录 ===', hist_records)  # 调试日志：打印待处理hist记录
        return hist_records
    
    #获取info_temp数据
    def get_info_temp_data(self):
        """
        查询现有info_temp记录（预警临时表），按ID降序取前100条，用于与hist数据比对合并
        """
        info_temp_sql = "SELECT id, type, codes, channel_names,names,yrdd_card_no, start_time, end_time FROM info_temp ORDER BY id DESC LIMIT 100"
        info_temp_records = list(self.execute_query(info_temp_sql))
        #print('=== 现有info_temp记录 ===', info_temp_records)  # 调试日志：打印现有预警临时记录
        return info_temp_records
    
    #计算结束时间方法
    def calculate_time_range(self):
        """
        计算结束时间（原有注释保留）
        根据配置参数计算结束时间        
        """
        config = self.get_early_warning_config() 
        
        if config is not None:
            times = config[0]['times']  # 时间阈值
            ex_time = config[0]['ex_time']  # 有效时间阈值（分钟）
            people_num = config[0]['people_num']  # 合并最小人数/车辆数阈值
        else:
            times = 30  # 默认次数阈值
            ex_time = 10  # 默认有效时间阈值（分钟）
            people_num = 2  # 默认最小合并数量（至少2个才触发合并）       
        print('=== 配置参数 ===', times,ex_time,people_num)             
       #计算结束时间=当前时间+配置参数中的时间阈值      
        end_time = datetime.now() + timedelta(minutes=times + ex_time)       
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S') 
        print('=== 结束时间 ===', end_time_str)      
        return end_time_str 
    
    
       

    
# 实例化预警数据处理类，供接口调用
c_ecyj = ecyj_tb()
def yddr(now_data = None,):  
    '''实现一点多人逻辑'''
    #查询hist表数据 where objType=5 limit 100;
    hist_records=c_ecyj.execute_query("SELECT * FROM wd_glsyj_xq_his WHERE objType=5 order by id desc LIMIT 1000")
    print(f'=== 待处理hist记录长度{len(hist_records)} ===')
    # hist_records = now_data
    #info_temp_records=c_ecyj.execute_query("SELECT * FROM info_temp where type='yddr' order by id desc LIMIT 100")
    #print('=== 待处理info_temp记录 ===', info_temp_records)
    
        
    #遍历hist表数据
    for hist_record in hist_records:
        id = hist_record['id']
        idstr = str(id)
        channel_id = hist_record['channelId']
        channel_name = hist_record['channelName']            
        carno = hist_record['cardNo']
        name = hist_record['objName']
        cap_timestr = hist_record['capTime']
        alarmTimeStr=hist_record['alarmTime']
        if name is None or name == '':
            continue
        print(name)
    
        # 转换captimestr字段将capTimestr与info_temp记录的时间段进行对比
        try:
            # 使用更灵活的方式解析时间字符串
            cap_time = datetime_string(cap_timestr)
            alarmTimeStr=datetime_string(alarmTimeStr)
        except ValueError as e:
            print(f"时间转换错误: {e}，原始时间字符串: {cap_timestr}")
            continue
        print(f"待处理hist记录 {id} 的channel_id {channel_id},cap_time: {cap_time}")
        #查询info_temp表数据中 hist_record 对应的 channel_id 的记录 是否存在于 info_temp中 条件 channel_id,cap_timestr in start_time, end_time,type = 'yddr'
        sql = f"SELECT * FROM info_temp WHERE codes like '%{channel_id}%'  AND ( '{cap_time}' BETWEEN start_time AND end_time ) AND type = 'yddr' order by id desc LIMIT 200"
        info_temp_records = c_ecyj.execute_query(sql) # 
        if len(info_temp_records) > 0:#存在
            print(f'=== 待处理info_temp记录 长度 {len(info_temp_records)} ===')
            info_record =info_temp_records[0] 
            # id 插入ids[],objName 插入names[],channelName插入channel_names[],cardNo插入yrdd_card_no[],wd_glsyj_xq_ids插入ids[],codes插入codes[]
            # info_record = json.loads(info_record)
            info_id = info_record['id']
            info_names = json.loads(info_record['names']) if info_record['names'] else []
            info_ids = json.loads(info_record['wd_glsyj_xq_ids']) if info_record['wd_glsyj_xq_ids'] else []  
            info_codes = json.loads(info_record['codes']) if info_record['codes'] else [] 
            
            start_time = info_record['start_time']
            end_time = info_record['end_time']
            
            
            print(f"匹配: hist记录 {id} 的channel_id {channel_id} 与 info记录 {info_record['id']} 的channel_id {info_codes} 一致")
            #3.进行数据合并
            merged_type = "yddr"
            
            #1.判断hist['id']是否在info_record['wd_glsyj_xq_ids']中
            if idstr not in info_ids:
                # people_num=
                # print(f"出现次数次有 {people_num} 个人")
                #4.执行数据更新表info_temp表：用MySQL的JSON_OBJECT构造JSON，避免重复转义
                try:
                    wd_glsyj_json = json.loads(info_record["wd_glsyj_json"])
                except json.JSONDecodeError as e:
                    wd_glsyj_json = []
                    print(f"{info_record["wd_glsyj_json"]}, /n wd_glsyj_json JSON解析错误: {e}")
                
                wd_glsyj_json.append(hist_record)
                
                names = json.loads(info_record["names"])
                names.append(name)
                
                yddr_card_no = json.loads(info_record["yddr_card_no"])
                yddr_card_no.append(carno)
                
                wd_glsyj_xq_ids = json.loads(info_record["wd_glsyj_xq_ids"])
                wd_glsyj_xq_ids.append(id)
                
                
                update_sql = f"""
                                UPDATE info_temp 
                                SET type = '{merged_type}', 
                                names = '{jsonToString(names)}', 
                                yddr_card_no = '{jsonToString(yddr_card_no)}',
                                wd_glsyj_xq_ids = '{jsonToString(wd_glsyj_xq_ids)}',
                                wd_glsyj_xq_num = json_array_append(wd_glsyj_xq_num, '$',{1}),
                                times='{alarmTimeStr}',
                                wd_glsyj_json = '{jsonToString(wd_glsyj_json)}',
                                update_time = NOW()
                                WHERE id = {info_id};
                                """
                c_ecyj.execute_update(update_sql)
                # print(f"合并成功：info_temp记录 {info_record['id']},sql: {update_sql}")
            else:
                print(info_names)
                index =  info_names.index(name)
                print(f"{name}在 id 为 {info_id}的数据 {info_names} 中所在位置为 {index}")
                wd_glsyj_xq_num = stringToJson(info_record['wd_glsyj_xq_num'])
                print(wd_glsyj_xq_num[index])
                wd_glsyj_xq_num[index] = int(wd_glsyj_xq_num[index]) + 1
                print(wd_glsyj_xq_num)
                
                update_sql = f"""
                                UPDATE info_temp 
                                set
                                wd_glsyj_xq_num = '{jsonToString(wd_glsyj_xq_num)}'
                                where id = {info_id}; 
                                """
                print(update_sql)           
                c_ecyj.execute_update(update_sql)              
                print(f"不合并:  {id}  存在 info记录 id为{info_id}的 {info_ids}数据中 ,计数+1")
              
        else: #不存在
            print(f"不匹配: hist记录 {id} 的时间 {cap_time} 不在 info记录中 记录长度 {len(info_temp_records)} ")
            end_time=c_ecyj.calculate_time_range()
            # print(f"记录{hist_record}")
            # # print(idstr)
            cap_time_str = datetime_string(hist_record['capTime'])
            
            # 简化wd_glsyj_json组装：复用字典，插入时直接json.dumps（仅一次转义）
            wd_glsyj_json = json.dumps({
                'id': idstr,
                'channelId': str(channel_id),
                'channelName': channel_name,
                'name': name,
                'cardNo': str(carno) if carno else '',
                'capTimestr': cap_time_str
            }, ensure_ascii=False)
            
            # wd_glsyj_json = hist_record
            
            print(wd_glsyj_json)
            
            c_ecyj.execute_update("INSERT INTO info_temp (type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,wd_glsyj_json,yddr_card_no, names, channel_names) VALUES ( %s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s,%s, %s, %s)",
                                (
                                    "yddr",1,jsonToString([channel_id]),alarmTimeStr,1,1, json.dumps([idstr]), cap_timestr,end_time,json.dumps([1]),jsonToString([wd_glsyj_json]),json.dumps([str(carno)]), jsonToString([name]),json.dumps([channel_name])
                                )
            )       
        
        
    return "执行成功"

# def yrdd():
#     '''实现一人多点逻辑'''
#     return 0

# def ycdq():
#     '''实现一人多点逻辑'''
#     return 0
# def yqdc():
#     '''实现一人多点逻辑'''
#     return 0
@ecyj.route('/process_hist_data', methods=['GET'])
def process_hist_data():
    """
    处理hist表数据的API接口（原有注释保留）
    对外提供GET请求接口，触发hist数据与info_temp的合并处理逻辑
    :return: JSON响应 - 处理成功返回结果，失败返回错误信息和500状态码
    """
    # try:
    #     # 调用数据处理核心方法
    #     result = yddr()
    #     return jsonify(result)  # 返回成功响应
    # except Exception as e:
    #     # 捕获异常，返回错误信息和500服务器错误状态码
    #     print(f"❌ 接口处理异常：{str(e)}")
    #     return jsonify({"error": str(e)}), 500
    result = yddr()
    return jsonify(result)  # 返回成功响应
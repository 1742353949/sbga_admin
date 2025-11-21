from app.models.base_db import MySQLHelper
from flask import Blueprint, jsonify
import logging
from datetime import datetime, timedelta

ecyj = Blueprint('ecyj', __name__, url_prefix='/ecyj')


# 1.创建数据库操作类
class ecyj_tb(MySQLHelper):
    def __init__(self):
        super().__init__()
        #self._tbname="wd_glsyj_xq_his"
       
    # def get_ecyj_list(self):
    #     #sql=f"select count(*) from xtuser"
    #     sql = "select * from wd_glsyj_xq_his where id=27449"
    #     result = self.execute_query(sql)
    #     #print(result)
    #     return result


    def get_enabled_configs(self):
        """
        从表3（wd_ecyj_yddr）获取所有启用的筛选配置
        👉 字段说明（直接对应数据库表3实际字段）：
            - times：基础时间段（分钟，如60）
            - min_count：最小记录数阈值（如5）
            - ex_time：有效时间（前后扩展分钟，如10）
            - status：配置启用状态（1=启用，0=禁用）
        :return: list - 启用的配置列表（字典格式，每个元素是一条配置）
        """
        # 存储启用的配置，如需启用语句加上WHERE status = 1  -- 表3实际字段：启用状态（1=启用）
        enabled_configs = []
        
        # 构造查询SQL：
        sql = f"""
            SELECT 
                id,  -- 配置ID（唯一标识）
                times,  -- 表3实际字段：基础时间段（分钟）
                people_num,    -- 表3实际字段：最小记录数阈值
                ex_time    -- 表3实际字段：有效时间（分钟）
            FROM wd_ecyj_yddr                
        """            
        # 执行SQL查询
        enabled_configs=self.execute_query(sql)
    
        print(enabled_configs)                 
        return enabled_configs
    
    
    def calculate_time_range(self, times, ex_time):
        """
        根据表3的配置，计算表1的查询时间范围
        时间范围规则：当前时间 - (基础时间段+有效时间) 至 当前时间 + 有效时间
        示例：times=60，ex_time=10 → 前70分钟至后10分钟
        :param times: int - 基础时间段（分钟，来自表3 times字段）
        :param ex_time: int - 有效时间（分钟，来自表3 ex_time字段）
        :return: tuple - (start_time_str, end_time_str) 数据库兼容的时间字符串（YYYY-MM-DD HH:MM:SS）
        """
        # 获取当前系统时间
        current_time = datetime.now()
        # 计算开始时间：当前时间 - (基础时间段+有效时间) 分钟
        start_time = current_time - timedelta(minutes=times + ex_time)
        # 计算结束时间：当前时间 + 有效时间 分钟
        end_time = current_time + timedelta(minutes=ex_time)
        # 转换为MySQL支持的时间字符串格式
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        # 返回时间范围字符串（供SQL查询使用）
        return start_time_str, end_time_str


    def get_qualified_channels(self, start_time, end_time, people_num):
        """
        从表1（wd_glsyj_xq_his）查询符合条件的摄像头编码（channelCode）
        👉 字段说明（直接对应数据库表1实际字段）：
            - capTime：采集时间（核心时间字段）
            - channelCode：摄像头编码（分组统计字段）
        筛选条件：1. 采集时间在计算的时间范围内；2. 同一channelCode的记录数≥最小阈值
        :param start_time: str - 查询开始时间（YYYY-MM-DD HH:MM:SS）
        :param end_time: str - 查询结束时间（YYYY-MM-DD HH:MM:SS）
        :param min_count: int - 最小记录数阈值（来自表3 min_count字段）
        :return: list - 符合条件的摄像头编码列表（字典格式，含channelCode和记录数）
        """
        # 初始化空列表，存储符合条件的摄像头编码
        qualified_channels = []
              
        # 构造SQL：直接使用表1实际字段名，无需映射
        sql = f"""
            SELECT 
                channelCode,  -- 表1实际字段：摄像头编码
                COUNT(*) AS record_count  -- 统计每组的记录数（别名统一为record_count）
            FROM wd_glsyj_xq_his
            WHERE 
                capTime BETWEEN %s AND %s  -- 表1实际字段：采集时间（时间范围筛选）
            GROUP BY channelCode  -- 按表1 channelCode字段分组
            HAVING COUNT(*) >= %s  -- 只保留记录数≥最小阈值的组
        """
        
        # 执行SQL（参数化查询，避免SQL注入风险）
        qualified_channels=self.execute_query(sql, (start_time, end_time, people_num))
        # 获取查询结果     
       
        return qualified_channels
    
    def get_channel_details(self, channel_code, start_time, end_time):
        """
        查询指定摄像头编码（channelCode）在时间范围内的所有详细记录（来自表1）
        👉 字段说明（直接对应数据库表1实际字段）：
            - capTime：采集时间
            - cardNo：身份证号码（统计计数字段）
        用于后续数据合并（如去重身份证号码、统计时间范围等）
        :param channel_code: str - 目标摄像头编码（表1 channelCode字段）
        :param start_time: str - 查询开始时间
        :param end_time: str - 查询结束时间
        :return: list - 该摄像头编码的详细记录列表（字典格式，含capTime和cardNo）
        """
        
        # 初始化空列表，存储摄像头详细记录
        details = []
                
        # 构造SQL：直接使用表1实际字段名，无需映射
        sql = f"""
            SELECT 
                capTime,  -- 表1实际字段：采集时间
                cardNo    -- 表1实际字段：身份证号码
            FROM wd_glsyj_xq_his
            WHERE 
                channelCode = %s  -- 筛选指定摄像头编码（表1 channelCode字段）
                AND capTime BETWEEN %s AND %s  -- 时间范围筛选（表1 capTime字段）
            ORDER BY capTime ASC  -- 按采集时间升序，方便后续取最早/最晚时间
        """
        
        # 执行参数化查询
        details=self.execute_query(sql, (channel_code, start_time, end_time))
       
        return details
    
    def merge_channel_data(self, channel_code, details):
        """
        合并指定摄像头编码的详细记录，生成表2（结果存储表）需要的结构化数据
        合并规则（核心）：
            1. 卡号去重：同一摄像头编码的卡号去重后用逗号拼接（如"card1,card2,card3"）
            2. 记录数统计：保留该摄像头编码的原始总记录数（含重复卡号）
            3. 时间范围：提取该摄像头编码记录的最早采集时间和最晚采集时间
            4. 防重复唯一键：生成摄像头编码编码+最早时间（分钟级）的唯一键（避免重复插入表2）
        参数：
            channel_code: str - 摄像头编码编码
            details: list - 该摄像头编码的详细记录（来自get_channel_details的结果）
        返回值：dict/None - 合并后的结构化数据（字典），无有效记录返回None
        """
        # 若没有详细记录，直接返回None（跳过后续插入）
        if not details:
            return None
        
        # 1. 卡号去重：用集合（set）自动去重（集合元素不可重复），再用逗号拼接为字符串
        unique_cards = ','.join({record['cardNo'] for record in details})
        
        # 2. 统计总记录数：直接取详细记录列表的长度（含重复卡号）
        total_count = len(details)
        
        # 3. 计算该摄像头编码记录的最早和最晚采集时间
        # 提取所有记录的capTime字段，转换为datetime对象（方便比较大小）
        cap_times = [datetime.strptime(record['capTime'], '%Y-%m-%d %H:%M:%S') for record in details]
        # 取最小时间（最早采集时间），转换为MySQL字符串格式
        cap_time_start = min(cap_times).strftime('%Y-%m-%d %H:%M:%S')
        # 取最大时间（最晚采集时间），转换为MySQL字符串格式
        cap_time_end = max(cap_times).strftime('%Y-%m-%d %H:%M:%S')
        
        # 4. 生成防重复唯一键：摄像头编码编码 + 最早时间（截取到分钟，避免秒级差异导致重复）
        # 例如：channel1_2025-11-21 14:30 → 同一摄像头编码同一分钟内的记录合并后只插入一次
        unique_key = f"{channel_code}_{cap_time_start[:16]}"
        
        # 返回合并后的结构化数据（字段与表2完全对应，方便插入）
        return {
            'channelCode': channel_code,                # 摄像头编码编码（与表2channelCode字段对应）
            'card_no_list': unique_cards,               # 去重后卡号列表（与表2card_no_list字段对应）
            'total_record_count': total_count,          # 总记录数（与表2total_record_count字段对应）
            'cap_time_start': cap_time_start,           # 最早采集时间（与表2cap_time_start字段对应）
            'cap_time_end': cap_time_end,               # 最晚采集时间（与表2cap_time_end字段对应）
            'unique_key': unique_key                    # 防重复唯一键（与表2unique_key字段对应）
        }

    def insert_into_table2(self, merged_data, config_id):
        """
        将合并后的结构化数据插入表2（wd_ecyj_info，结果存储表）
        核心特性：支持防重复插入（依赖表2的unique_key唯一索引），若唯一键已存在则更新最新数据
        参数：
            merged_data: dict - 合并后的结构化数据（来自merge_channel_data的结果）
            config_id: int - 关联的表3配置ID（用于追溯该记录是哪个筛选规则生成的）
        返回值：bool - 插入/更新成功返回True，失败返回False
        SQL逻辑：INSERT ... ON DUPLICATE KEY UPDATE → 存在则更新，不存在则插入
        """
        # 若合并数据为空，直接返回False（跳过插入）
        if not merged_data:
            return False
        
        
        # SQL插入语句：插入合并后的数据，存在重复唯一键则更新
        sql = """
            INSERT INTO wd_ecyj_info (
                channelCode,          -- 摄像头编码编码（来自表1）
                card_no_list,         -- 去重后卡号列表（合并后）
                total_record_count,   -- 总记录数（合并后）
                cap_time_start,       -- 最早采集时间（合并后）
                cap_time_end,         -- 最晚采集时间（合并后）
                config_id,            -- 关联表3的配置ID（追溯筛选规则）
                create_time,          -- 插入表2的时间（当前系统时间）
                unique_key            -- 防重复唯一键（用于去重）
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)  -- 参数占位符（与字段顺序一一对应）
            -- 关键：若unique_key已存在（重复），更新以下字段为最新值（避免重复插入，保持数据新鲜）
            ON DUPLICATE KEY UPDATE 
                card_no_list = VALUES(card_no_list),          -- 更新卡号列表（可能新增卡号）
                total_record_count = VALUES(total_record_count),  -- 更新总记录数（可能增加）
                cap_time_end = VALUES(cap_time_end),          -- 更新最晚采集时间（可能延后）
                create_time = VALUES(create_time)             -- 更新插入时间（记录最新同步时间）
        """
        # 获取当前系统时间（作为插入表2的create_time字段值）
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 构造SQL参数（与VALUES占位符顺序严格对应，避免字段错位）
        sql_params = (
            merged_data['channelCode'],          # 摄像头编码编码
            merged_data['card_no_list'],         # 去重卡号列表
            merged_data['total_record_count'],   # 总记录数
            merged_data['cap_time_start'],       # 最早采集时间
            merged_data['cap_time_end'],         # 最晚采集时间
            config_id,                           # 关联表3配置ID
            current_time,                        # 插入时间
            merged_data['unique_key']            # 防重复唯一键
        )
        # 执行SQL插入语句（传入参数）
        self.execute_update(sql, sql_params)
        # 提交事务（MySQL默认关闭自动提交，增删改操作需手动提交才生效）
        
        
       
    
# 实例化数据库操作类
c_ecyj= ecyj_tb()


@ecyj.route('/ecyjtest')
def ecyjtest():
    try:
        result =c_ecyj.get_channel_details
        return jsonify({
            "code": 200,
            "data": result,
            "message": "success"
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "data": [],
            "message": str(e)
        }), 500
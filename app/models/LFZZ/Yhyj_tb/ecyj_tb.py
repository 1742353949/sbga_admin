################################################################################
# 模块名：ecyj_tb
# 功能：联防智治平台 隐患预警模块数据处理
# 作者：jkf
# 时间：2025-12-04
##########

# 导入数据库操作基础类，提供数据库连接和CRUD核心能力
from app.models.base_db import MySQLHelper

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
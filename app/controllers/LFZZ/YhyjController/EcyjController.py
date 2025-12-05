################################################################################
# 模块名：EcyjController
# 功能：联防智治平台 隐患预警模块逻辑处理控制器
# 作者：jkf
# 时间：2025-12-04
##########


# 导入日期时间处理模块，用于时间格式转换和时间段计算
from datetime import datetime, timedelta
# 导入JSON模块，用于处理codes/names字段的序列化与反序列化
import json
from app.helper.helper import *
# 导入数据表类
from app.models.LFZZ.Yhyj_tb.ecyj_tb import ecyj_tb


# 实例化预警数据处理类，供接口调用
tb_ecyj = ecyj_tb()

class EcyjController():
    
    def __init__(self):
        """初始化控制器，加载配置参数"""
        config = tb_ecyj.get_early_warning_config()
        if config is not None and len(config) > 0:
            self.p_num = config[0]['people_num']
            self.times = config[0]['times']
            self.ex_time = config[0]['ex_time']
        else:
            self.p_num = 2
            self.times = 30
            self.ex_time = 10

    #计算结束时间方法
    def calculate_time_range(self, alarmTimeStr):
        """
        计算结束时间
        根据配置参数计算结束时间        
        """
        #print('=== 配置参数 ===', self.times, self.ex_time, self.p_num)             
        # 计算结束时间=当前时间+配置参数中的时间阈值      
        end_time = alarmTimeStr + timedelta(minutes=self.times + self.ex_time)       
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S') 
        #print('=== 结束时间 ===', end_time_str)      
        return end_time_str
    # def calculate_time_range(self,alarmTimeStr):
    #     """
    #     计算结束时间（原有注释保留）
    #     根据配置参数计算结束时间        
    #     """
    #     config = tb_ecyj.get_early_warning_config()
    #     #p_num = config[0]['people_num'] 
        
    #     if config is not None:
    #         times = config[0]['times']  # 时间阈值
    #         ex_time = config[0]['ex_time']  # 有效时间阈值（分钟）
    #         p_num = config[0]['people_num']  # 合并最小人数/车辆数阈值
    #     else:
    #         times = 30  # 默认次数阈值
    #         ex_time = 10  # 默认有效时间阈值（分钟）
    #         p_num = 2  # 默认最小合并数量（至少2个才触发合并）       
    #     #print('=== 配置参数 ===', times,ex_time,people_num)             
    #    #计算结束时间=当前时间+配置参数中的时间阈值      
    #     end_time = alarmTimeStr + timedelta(minutes=times + ex_time)       
    #     end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S') 
    #     #print('=== 结束时间 ===', end_time_str)      
    #     return end_time_str 
    
    def yddr(self,now_data = None,num_people=None):  
        '''实现一点多人逻辑'''
        #删除hist表中name为空或空字符串的无效数据，避免无效数据干扰合并逻辑
        delete_empty_sql = "DELETE FROM hist WHERE name IS NULL OR name = ''order by id desc limit 1000"
        tb_ecyj.execute_update(delete_empty_sql)
        #查询hist表数据 where objType=5 limit 100;
        hist_records=tb_ecyj.execute_query("SELECT * FROM wd_glsyj_xq_his WHERE objType=5 order by capTime asc LIMIT 1000")
        #print(f'=== 待处理hist记录长度{len(hist_records)} ===')
        # hist_records = now_data
        #info_temp_records=tb_ecyj.execute_query("SELECT * FROM info_temp where type='yddr' order by id desc LIMIT 100")
        #print('=== 待处理info_temp记录 ===', info_temp_records)
        
            
        #遍历hist表数据
        for hist_record in hist_records:
            id = hist_record['id']
            idstr = str(id)
            channel_id = hist_record['channelId']
            channel_name = hist_record['channelName']            
            carno = hist_record['cardNo']
            name = hist_record['objName']
            #cap_timestr = hist_record['capTime']
            alarmTimeStr=hist_record['alarmTime']
            #alarmTime=hist_record['alarmTime']
            if name is None or name == '':
                continue
            #print(name)
        
            # 转换captimestr字段将capTimestr与info_temp记录的时间段进行对比
            try:
                # 使用更灵活的方式解析时间字符串
                #cap_time = datetime_string(alarmTimeStr)
                alarmTimeStr=datetime_string(alarmTimeStr)
            except ValueError as e:
                print(f"时间转换错误: {e}，原始时间字符串: {alarmTimeStr}")
                continue
            #print(f"待处理hist记录 {id} 的channel_id {channel_id},cap_time: {cap_time}")
            #查询info_temp表数据中 hist_record 对应的 channel_id 的记录 是否存在于 info_temp中 条件 channel_id,cap_timestr in start_time, end_time,type = 'yddr'
            sql = f"SELECT * FROM info_temp WHERE codes like '%{channel_id}%'  AND ( '{alarmTimeStr}' BETWEEN start_time AND end_time ) AND type = 'yddr' order by id desc  LIMIT 200"
            info_temp_records = tb_ecyj.execute_query(sql) # 
            if len(info_temp_records) > 0:#存在
                #print(f'=== 待处理info_temp记录 长度 {len(info_temp_records)} ===')
                info_record =info_temp_records[0] 
                # id 插入ids[],objName 插入names[],channelName插入channel_names[],cardNo插入yrdd_card_no[],wd_glsyj_xq_ids插入ids[],codes插入codes[]
                # info_record = json.loads(info_record)
                info_id = info_record['id']
                info_names = json.loads(info_record['names']) if info_record['names'] else []
                info_ids = json.loads(info_record['wd_glsyj_xq_ids']) if info_record['wd_glsyj_xq_ids'] else []  
                info_codes = json.loads(info_record['codes']) if info_record['codes'] else [] 
                people_num=info_record['people_num']
                start_time = info_record['start_time']
                end_time = info_record['end_time']
                
                
                #print(f"匹配: hist记录 {id} 的channel_id {channel_id} 与 info记录 {info_record['id']} 的channel_id {info_codes} 一致")
                #3.进行数据合并
                
                
                #1.判断hist['id']是否在info_record['wd_glsyj_xq_ids']中
                if idstr not in info_ids:
                    # people_num=
                    # print(f"出现次数次有 {people_num} 个人")
                    #4.执行数据更新表info_temp表：用MySQL的JSON_OBJECT构造JSON，避免重复转义
                    
                    names = json.loads(info_record["names"])
                    names.append(name)
                    
                    yddr_card_no = json.loads(info_record["yddr_card_no"])
                    yddr_card_no.append(carno)
                    
                    wd_glsyj_xq_ids = json.loads(info_record["wd_glsyj_xq_ids"])
                    wd_glsyj_xq_ids.append(f'{id}')
                    
                    if name in info_names:
                        #print(f"{name} 不在 id 为 {info_id}的数据 {info_names} 中")
                        #print(info_names)
                        index =  info_names.index(name)
                        #print(f"{name}在 id 为 {info_id}的数据 {info_names} 中所在位置为 {index}")
                        wd_glsyj_xq_num = stringToJson(info_record['wd_glsyj_xq_num'])
                        #print(wd_glsyj_xq_num[index])
                        wd_glsyj_xq_num[index] = int(wd_glsyj_xq_num[index]) + 1
                        #print(wd_glsyj_xq_num)
                        
                        update_sql = f"""
                                        UPDATE info_temp 
                                        set
                                        wd_glsyj_xq_num = '{jsonToString(wd_glsyj_xq_num)}'
                                        where id = {info_id}; 
                                        """
                        #print(update_sql)           
                        tb_ecyj.execute_update(update_sql)              
                        #print(f"不合并:  {id}  存在 info记录 id为{info_id}的 {info_ids}数据中 ,计数+1")
                    else:
                        update_sql = f"""
                                        UPDATE info_temp 
                                        SET type = 'yddr', 
                                        names = '{jsonToString(names)}', 
                                        yddr_card_no = '{jsonToString(yddr_card_no)}',
                                        wd_glsyj_xq_ids = '{jsonToString(wd_glsyj_xq_ids)}',
                                        wd_glsyj_xq_num = json_array_append(wd_glsyj_xq_num, '$',{1}),
                                        times=NOW(),
                                        update_time = NOW()
                                        WHERE id = {info_id};
                                        """
                        tb_ecyj.execute_update(update_sql)
                    # print(f"合并成功：info_temp记录 {info_record['id']},sql: {update_sql}")
                    
                    
                #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
                # 直接获取配置文件的people_num值  
                # config = tb_ecyj.get_early_warning_config()
                # config_num = config[0]['people_num'] 
                #print('=== 人数阈值 ===', self.p_num)
                if people_num >= self.p_num:                 
                    print(f"达到阈值: info_temp id为 {info_id}")
                    #print(people_num >= self.p_num)
                    cx_sql = tb_ecyj.execute_query(f"select * from info where id ={info_id}")
                    
                    #print(len(cx_sql))
                    
                    if len(cx_sql)==0:
                        #print(info_id not in cx_sql)                
                        #获取info_temp中id为{info_id}的记录写入info表                
                        inster_sql = f"""
                                        INSERT INTO info (id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names) 
                                        (SELECT id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names FROM info_temp WHERE id = {info_id})
                                        """
                        tb_ecyj.execute_update(inster_sql)
                        print(f"插入成功: info_temp id为 {info_id} 出现{people_num}次")
                    else: #已经存在
                        #更新info中存在的info_temp记录
                        # 如果info表中有唯一键约束（如id为主键）,直接复制info_temp记录到info表
                        insert_sql = """
                            INSERT INTO info (id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names)
                            SELECT id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names
                            FROM info_temp 
                            WHERE id = %s
                            ON DUPLICATE KEY UPDATE
                                type = VALUES(type),
                                wd_ecyj_id = VALUES(wd_ecyj_id),
                                codes = VALUES(codes),
                                times = VALUES(times),
                                people_num = VALUES(people_num),
                                dw_num = VALUES(dw_num),
                                wd_glsyj_xq_ids = VALUES(wd_glsyj_xq_ids),
                                start_time = VALUES(start_time),
                                end_time = VALUES(end_time),
                                wd_glsyj_xq_num = VALUES(wd_glsyj_xq_num),
                                car_nos = VALUES(car_nos),
                                names = VALUES(names),
                                channel_names = VALUES(channel_names)
                        """

                        tb_ecyj.execute_update(insert_sql, (info_id,))
                        
                        print(f"id {info_id}在 info 中已经存在，进行更新") 
                
            else: #不存在
                #print(f"不匹配: hist记录 {id} 的时间 {alarmTimeStr} 不在 info记录中 记录长度 {len(info_temp_records)} ")
                endtime=self.calculate_time_range(alarmTimeStr)
                sql = f"SELECT * FROM info_temp WHERE codes like '%{channel_id}%'  AND start_time like '%{alarmTimeStr}%'  AND type = 'yddr'  LIMIT 200"
                qc_info_temp_records = tb_ecyj.execute_query(sql)
                if len(qc_info_temp_records) > 0: #存在
                    continue
                else: #不存在
                
                    tb_ecyj.execute_update("INSERT INTO info_temp (type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,yddr_card_no, names, channel_names) VALUES ( %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)",
                                        (
                                            "yddr",1,jsonToString([channel_id]),datetime.now(),1,1,jsonToString([idstr]), alarmTimeStr,endtime,jsonToString([1]),jsonToString([carno]), jsonToString([name]),jsonToString([channel_name])
                                        )
                    )       
            
            #判断当前id 记录end_time 是否结束 

            #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
            
        return "执行成功"

    def yrdd(self):
        '''实现一人多点逻辑'''
        #查询hist表数据 where objType=5 limit 100;
        hist_records=tb_ecyj.execute_query("SELECT * FROM wd_glsyj_xq_his WHERE objType=5 order by capTime asc LIMIT 1000")
        #print(f'=== 待处理hist记录长度{len(hist_records)} ===')
        # hist_records = now_data
        #info_temp_records=tb_ecyj.execute_query("SELECT * FROM info_temp where type='yrdd' order by id desc LIMIT 100")
        #print('=== 待处理info_temp记录 ===', info_temp_records)
        
            
        #遍历hist表数据
        for hist_record in hist_records:
            id = hist_record['id']
            idstr = str(id)
            channel_id = hist_record['channelId']
            channel_name = hist_record['channelName']            
            carno = hist_record['cardNo']
            name = hist_record['objName']
            #cap_timestr = hist_record['capTime']
            alarmTimeStr=hist_record['alarmTime']
            #alarmTime=hist_record['alarmTime']
            
            #跳过无姓名的记录
            if name is None or name == '':
                continue
           
        
            # 转换captimestr字段将capTimestr与info_temp记录的时间段进行对比
            try:
                # 使用更灵活的方式解析时间字符串
                #cap_time = datetime_string(cap_timestr)
                alarmTimeStr=datetime_string(alarmTimeStr)
            except ValueError as e:
                print(f"时间转换错误: {e}，原始时间字符串: {alarmTimeStr}")
                continue
            
            #print(f"待处理hist记录 {id} 的objname {name},alarmTimeStr: {alarmTimeStr}")
            #查询info_temp表数据中 hist_record 对应的 name 的记录 是否存在于 info_temp中 条件 names,alarmTimeStr in start_time, end_time,type = 'yrdd'
            sql = f"SELECT * FROM info_temp WHERE names like '%{name}%'  AND ( '{alarmTimeStr}' BETWEEN start_time AND end_time ) AND type = 'yrdd' order by id desc  LIMIT 200"
            info_temp_records = tb_ecyj.execute_query(sql) # 
            if len(info_temp_records) > 0:#存在
                ##print(f'=== 待处理info_temp记录 长度 {len(info_temp_records)} ===')
                info_record =info_temp_records[0] 
                # id 插入ids[],objName 插入names[],channelName插入channel_names[],cardNo插入yrdd_card_no[],wd_glsyj_xq_ids插入ids[],codes插入codes[]
                # info_record = json.loads(info_record)
                info_id = info_record['id']
                info_names = json.loads(info_record['names']) if info_record['names'] else []
                info_ids = json.loads(info_record['wd_glsyj_xq_ids']) if info_record['wd_glsyj_xq_ids'] else []  
                info_codes = json.loads(info_record['codes']) if info_record['codes'] else [] 
                people_num=info_record['people_num']
                
                
                #print(f"匹配: hist记录 {id} 的objname {name} 与 info记录 {info_record['id']} 的names {info_names} 一致")
                #进行数据合并             
                          
                #1.判断hist['id']是否在info_record['wd_glsyj_xq_ids']中
                if idstr not in info_ids:
                    
                    #4.执行数据更新表info_temp表：用MySQL的JSON_OBJECT构造JSON，避免重复转义
                    codes = json.loads(info_record["codes"])
                    codes.append(channel_id)
                    
                    wd_glsyj_xq_ids = json.loads(info_record["wd_glsyj_xq_ids"])
                    wd_glsyj_xq_ids.append(f'{id}')
                    
                    channel_names = json.loads(info_record["channel_names"])
                    channel_names.append(channel_name)
                    
                    if channel_id in info_codes:
                        #print(f"{channel_id} 在 id 为 {info_id}的数据 {info_codes} 中")
                        #print(info_codes)
                        index =  info_codes.index(channel_id)
                        #print(f"{channel_id}在 id 为 {info_id}的数据 {info_codes} 中所在位置为 {index}")
                        wd_glsyj_xq_num = stringToJson(info_record['wd_glsyj_xq_num'])
                        #print(wd_glsyj_xq_num[index])
                        wd_glsyj_xq_num[index] = int(wd_glsyj_xq_num[index]) + 1
                        #print(wd_glsyj_xq_num)
                        
                        update_sql = f"""
                                        UPDATE info_temp 
                                        set
                                        wd_glsyj_xq_num = '{jsonToString(wd_glsyj_xq_num)}'
                                        where id = {info_id}; 
                                        """
                        #print(update_sql)           
                        tb_ecyj.execute_update(update_sql)              
                        #print(f"不合并:  {id}  存在 info记录 id为{info_id}的 {info_ids}数据中 ,计数+1")
                    else:
                        update_sql = f"""
                                        UPDATE info_temp 
                                        SET type = 'yrdd', 
                                        codes = '{jsonToString(codes)}', 
                                        channel_names = '{jsonToString(channel_names)}',                                        
                                        wd_glsyj_xq_ids = '{jsonToString(wd_glsyj_xq_ids)}',
                                        wd_glsyj_xq_num = json_array_append(wd_glsyj_xq_num, '$',{1}),
                                        times=NOW(),
                                        update_time = NOW()
                                        WHERE id = {info_id};
                                        """
                        tb_ecyj.execute_update(update_sql)
                    #print(f"合并成功：info_temp记录 {info_record['id']},sql: {update_sql}")
                    
                    
                #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
                # 直接获取配置文件的people_num值  
                # config = tb_ecyj.get_early_warning_config()
                # config_num = config[0]['people_num'] 
                #print('=== 人数阈值 ===', self.p_num)
                if people_num >= self.p_num:                 
                    print(f"达到阈值: info_temp id为 {info_id}")
                    #print(people_num >= self.p_num)
                    cx_sql = tb_ecyj.execute_query(f"select * from info where id ={info_id}")
                    
                    #print(len(cx_sql))
                    
                    if len(cx_sql)==0:
                        #print(info_id not in cx_sql)                
                        #获取info_temp中id为{info_id}的记录写入info表                
                        inster_sql = f"""
                                        INSERT INTO info (id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names) 
                                        (SELECT id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names FROM info_temp WHERE id = {info_id})
                                        """
                        tb_ecyj.execute_update(inster_sql)
                        print(f"插入成功: info_temp id为 {info_id} 出现{people_num}次")
                    else: #已经存在
                        #更新info中存在的info_temp记录
                        # 如果info表中有唯一键约束（如id为主键）,直接复制info_temp记录到info表
                        insert_sql = """
                            INSERT INTO info (id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names)
                            SELECT id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names
                            FROM info_temp 
                            WHERE id = %s
                            ON DUPLICATE KEY UPDATE
                                type = VALUES(type),
                                wd_ecyj_id = VALUES(wd_ecyj_id),
                                codes = VALUES(codes),
                                times = VALUES(times),
                                people_num = VALUES(people_num),
                                dw_num = VALUES(dw_num),
                                wd_glsyj_xq_ids = VALUES(wd_glsyj_xq_ids),
                                start_time = VALUES(start_time),
                                end_time = VALUES(end_time),
                                wd_glsyj_xq_num = VALUES(wd_glsyj_xq_num),
                                car_nos = VALUES(car_nos),
                                names = VALUES(names),
                                channel_names = VALUES(channel_names)
                        """

                        tb_ecyj.execute_update(insert_sql, (info_id,))
                        
                        print(f"id {info_id}在 info 中已经存在，进行更新") 
                
            else: #不存在
                #print(f"不匹配: hist记录 {id} 的时间 {cap_time} 不在 info记录中 记录长度 {len(info_temp_records)} ")                
                endtime=self.calculate_time_range(alarmTimeStr)
                sql = f"SELECT * FROM info_temp WHERE names like '%{name}%'  AND start_time like '%{alarmTimeStr}%'  AND type = 'yrdd'  LIMIT 200"
                qc_info_temp_records = tb_ecyj.execute_query(sql)
                if len(qc_info_temp_records) > 0: #存在
                    continue
                else: #不存在
                    
                    # return 0
                    tb_ecyj.execute_update("INSERT INTO info_temp (type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,yrdd_card_no, names, channel_names) VALUES ( %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)",
                                        (
                                            "yrdd",1,jsonToString([channel_id]),datetime.now(),1,1,jsonToString([idstr]), alarmTimeStr,endtime,jsonToString([1]),jsonToString([carno]), jsonToString([name]),jsonToString([channel_name])
                                        )
                    )       
            
            #判断当前id 记录end_time 是否结束 

            #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
            
        return "执行成功"

    def ycdq(self):   
        '''实现一车多区逻辑''' 
        #查询hist表数据 where objType=1 limit 100;
        hist_records=tb_ecyj.execute_query("SELECT * FROM wd_glsyj_xq_his WHERE objType=1 order by capTime asc LIMIT 1000")
        #print(f'=== 待处理hist记录长度{len(hist_records)} ===')
        # hist_records = now_data
        #info_temp_records=tb_ecyj.execute_query("SELECT * FROM info_temp where type='yrdd' order by id desc LIMIT 100")
        #print('=== 待处理info_temp记录 ===', info_temp_records)
        
            
        #遍历hist表数据
        for hist_record in hist_records:
            id = hist_record['id']
            idstr = str(id)
            channel_id = hist_record['channelId']
            channel_name = hist_record['channelName']            
            carno = hist_record['cardNo']
            name = hist_record['objName']
            #cap_timestr = hist_record['capTime']
            alarmTimeStr=hist_record['alarmTime']
            #alarmTime=hist_record['alarmTime']
            
            #跳过无姓名的记录
            if name is None or name == '':
                continue
           
        
            # 转换captimestr字段将capTimestr与info_temp记录的时间段进行对比
            try:
                # 使用更灵活的方式解析时间字符串
                #cap_time = datetime_string(cap_timestr)
                alarmTimeStr=datetime_string(alarmTimeStr)
            except ValueError as e:
                print(f"时间转换错误: {e}，原始时间字符串: {alarmTimeStr}")
                continue
            
            #print(f"待处理hist记录 {id} 的objname {name},alarmTimeStr: {alarmTimeStr}")
            #查询info_temp表数据中 hist_record 对应的 name 的记录 是否存在于 info_temp中 条件 names,alarmTimeStr in start_time, end_time,type = 'yrdd'
            sql = f"SELECT * FROM info_temp WHERE names like '%{name}%'  AND ( '{alarmTimeStr}' BETWEEN start_time AND end_time ) AND type = 'ycdq' order by id desc  LIMIT 200"
            info_temp_records = tb_ecyj.execute_query(sql) # 
            if len(info_temp_records) > 0:#存在
                ##print(f'=== 待处理info_temp记录 长度 {len(info_temp_records)} ===')
                info_record =info_temp_records[0] 
                # id 插入ids[],objName 插入names[],channelName插入channel_names[],cardNo插入yrdd_card_no[],wd_glsyj_xq_ids插入ids[],codes插入codes[]
                # info_record = json.loads(info_record)
                info_id = info_record['id']
                info_names = json.loads(info_record['names']) if info_record['names'] else []
                info_ids = json.loads(info_record['wd_glsyj_xq_ids']) if info_record['wd_glsyj_xq_ids'] else []  
                info_codes = json.loads(info_record['codes']) if info_record['codes'] else [] 
                people_num=info_record['people_num']
                
                
                #print(f"匹配: hist记录 {id} 的objname {name} 与 info记录 {info_record['id']} 的names {info_names} 一致")
                #进行数据合并             
                          
                #1.判断hist['id']是否在info_record['wd_glsyj_xq_ids']中
                if idstr not in info_ids:
                    
                    #4.执行数据更新表info_temp表：用MySQL的JSON_OBJECT构造JSON，避免重复转义
                    codes = json.loads(info_record["codes"])
                    codes.append(channel_id)
                    
                    wd_glsyj_xq_ids = json.loads(info_record["wd_glsyj_xq_ids"])
                    wd_glsyj_xq_ids.append(f'{id}')
                    
                    channel_names = json.loads(info_record["channel_names"])
                    channel_names.append(channel_name)
                    
                    if channel_id in info_codes:
                        #print(f"{channel_id} 在 id 为 {info_id}的数据 {info_codes} 中")
                        #print(info_codes)
                        index =  info_codes.index(channel_id)
                        #print(f"{channel_id}在 id 为 {info_id}的数据 {info_codes} 中所在位置为 {index}")
                        wd_glsyj_xq_num = stringToJson(info_record['wd_glsyj_xq_num'])
                        #print(wd_glsyj_xq_num[index])
                        wd_glsyj_xq_num[index] = int(wd_glsyj_xq_num[index]) + 1
                        #print(wd_glsyj_xq_num)
                        
                        update_sql = f"""
                                        UPDATE info_temp 
                                        set
                                        wd_glsyj_xq_num = '{jsonToString(wd_glsyj_xq_num)}'
                                        where id = {info_id}; 
                                        """
                        #print(update_sql)           
                        tb_ecyj.execute_update(update_sql)              
                        #print(f"不合并:  {id}  存在 info记录 id为{info_id}的 {info_ids}数据中 ,计数+1")
                    else:
                        update_sql = f"""
                                        UPDATE info_temp 
                                        SET type = 'ycdq', 
                                        codes = '{jsonToString(codes)}', 
                                        channel_names = '{jsonToString(channel_names)}',                                        
                                        wd_glsyj_xq_ids = '{jsonToString(wd_glsyj_xq_ids)}',
                                        wd_glsyj_xq_num = json_array_append(wd_glsyj_xq_num, '$',{1}),
                                        times=NOW(),
                                        update_time = NOW()
                                        WHERE id = {info_id};
                                        """
                        tb_ecyj.execute_update(update_sql)
                    #print(f"合并成功：info_temp记录 {info_record['id']},sql: {update_sql}")
                    
                    
                #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
                # 直接获取配置文件的people_num值  
                # config = tb_ecyj.get_early_warning_config()
                # config_num = config[0]['people_num'] 
                #print('=== 人数阈值 ===', self.p_num)
                if people_num >= self.p_num:                 
                    print(f"达到阈值: info_temp id为 {info_id}")
                    #print(people_num >= self.p_num)
                    cx_sql = tb_ecyj.execute_query(f"select * from info where id ={info_id}")
                    
                    #print(len(cx_sql))
                    
                    if len(cx_sql)==0:
                        #print(info_id not in cx_sql)                
                        #获取info_temp中id为{info_id}的记录写入info表                
                        inster_sql = f"""
                                        INSERT INTO info (id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names) 
                                        (SELECT id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names FROM info_temp WHERE id = {info_id})
                                        """
                        tb_ecyj.execute_update(inster_sql)
                        print(f"插入成功: info_temp id为 {info_id} 出现{people_num}次")
                    else: #已经存在
                        #更新info中存在的info_temp记录
                        # 如果info表中有唯一键约束（如id为主键）,直接复制info_temp记录到info表
                        insert_sql = """
                            INSERT INTO info (id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names)
                            SELECT id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names
                            FROM info_temp 
                            WHERE id = %s
                            ON DUPLICATE KEY UPDATE
                                type = VALUES(type),
                                wd_ecyj_id = VALUES(wd_ecyj_id),
                                codes = VALUES(codes),
                                times = VALUES(times),
                                people_num = VALUES(people_num),
                                dw_num = VALUES(dw_num),
                                wd_glsyj_xq_ids = VALUES(wd_glsyj_xq_ids),
                                start_time = VALUES(start_time),
                                end_time = VALUES(end_time),
                                wd_glsyj_xq_num = VALUES(wd_glsyj_xq_num),
                                car_nos = VALUES(car_nos),
                                names = VALUES(names),
                                channel_names = VALUES(channel_names)
                        """

                        tb_ecyj.execute_update(insert_sql, (info_id,))
                        
                        print(f"id {info_id}在 info 中已经存在，进行更新") 
                else: #不存在
                        print(f"id {info_id}在 info 中不存在")
                        continue
                
            else: #不存在
                #print(f"不匹配: hist记录 {id} 的时间 {cap_time} 不在 info记录中 记录长度 {len(info_temp_records)} ")                
                endtime=self.calculate_time_range(alarmTimeStr)
                sql = f"SELECT * FROM info_temp WHERE names like '%{name}%'  AND start_time like '%{alarmTimeStr}%'  AND type = 'ycdq'  LIMIT 200"
                qc_info_temp_records = tb_ecyj.execute_query(sql)
                if len(qc_info_temp_records) > 0: #存在
                    continue
                else: #不存在
                    
                    # return 0
                    tb_ecyj.execute_update("INSERT INTO info_temp (type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num, names,car_no, channel_names) VALUES ( %s, %s, %s, %s, %s, %s,%s, %s, %s,%s, %s, %s,%s)",
                                        (
                                            "ycdq",1,jsonToString([channel_id]),datetime.now(),1,1,jsonToString([idstr]), alarmTimeStr,endtime,jsonToString([1]), jsonToString([name]),name,jsonToString([channel_name])
                                        )
                    )       
            
            #判断当前id 记录end_time 是否结束 

            #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 否 删除该记录（是否删除无效数据）
            
        return "执行成功"
    
    def yqdc(self):
        '''实现一区多车逻辑'''
        #删除hist表中name为空或空字符串的无效数据，避免无效数据干扰合并逻辑
        delete_empty_sql = "DELETE FROM hist WHERE name IS NULL OR name = ''order by id desc limit 1000"
        tb_ecyj.execute_update(delete_empty_sql)
        #查询hist表数据 where objType=1 limit 100;
        hist_records=tb_ecyj.execute_query("SELECT * FROM wd_glsyj_xq_his WHERE objType=1 order by capTime asc LIMIT 1000")
        #print(f'=== 待处理hist记录长度{len(hist_records)} ===')
        # hist_records = now_data
        #info_temp_records=tb_ecyj.execute_query("SELECT * FROM info_temp where type='yqdc' order by id desc LIMIT 100")
        #print('=== 待处理info_temp记录 ===', info_temp_records)
        
            
        #遍历hist表数据
        for hist_record in hist_records:
            id = hist_record['id']
            idstr = str(id)
            channel_id = hist_record['channelId']
            channel_name = hist_record['channelName']            
            carno = hist_record['cardNo']
            name = hist_record['objName']
            #cap_timestr = hist_record['capTime']
            alarmTimeStr=hist_record['alarmTime']
            #alarmTime=hist_record['alarmTime']
            if name is None or name == '':
                continue
            #print(name)
        
            # 转换captimestr字段将capTimestr与info_temp记录的时间段进行对比
            try:
                # 使用更灵活的方式解析时间字符串
                #cap_time = datetime_string(alarmTimeStr)
                alarmTimeStr=datetime_string(alarmTimeStr)
            except ValueError as e:
                print(f"时间转换错误: {e}，原始时间字符串: {alarmTimeStr}")
                continue
            #print(f"待处理hist记录 {id} 的channel_id {channel_id},cap_time: {cap_time}")
            #查询info_temp表数据中 hist_record 对应的 channel_id 的记录 是否存在于 info_temp中 条件 channel_id,cap_timestr in start_time, end_time,type = 'yqdc'
            sql = f"SELECT * FROM info_temp WHERE codes like '%{channel_id}%'  AND ( '{alarmTimeStr}' BETWEEN start_time AND end_time ) AND type = 'yqdc' order by id desc LIMIT 500"
            info_temp_records = tb_ecyj.execute_query(sql) # 
            if len(info_temp_records) > 0:#存在
                #print(f'=== 待处理info_temp记录 长度 {len(info_temp_records)} ===')
                info_record =info_temp_records[0] 
                # id 插入ids[],objName 插入names[],channelName插入channel_names[],cardNo插入yrdd_card_no[],wd_glsyj_xq_ids插入ids[],codes插入codes[]
                # info_record = json.loads(info_record)
                info_id = info_record['id']
                info_names = json.loads(info_record['names']) if info_record['names'] else []
                info_ids = json.loads(info_record['wd_glsyj_xq_ids']) if info_record['wd_glsyj_xq_ids'] else []  
                info_codes = json.loads(info_record['codes']) if info_record['codes'] else [] 
                people_num=info_record['people_num']
                info_xq_num=info_record['wd_glsyj_xq_num']
                start_time = info_record['start_time']
                end_time = info_record['end_time']
                
                #print(f"匹配: hist记录 {id} 的channel_id {channel_id} 与 info记录 {info_record['id']} 的channel_id {info_codes} 一致")
                #3.进行数据合并
                
                #1.判断hist['id']是否在info_record['wd_glsyj_xq_ids']中
                if idstr not in info_ids:
                                       
                    names = json.loads(info_record["names"])
                    names.append(name)
                    
                    wd_glsyj_xq_ids = json.loads(info_record["wd_glsyj_xq_ids"])
                    wd_glsyj_xq_ids.append(f'{id}')
                    
                    if name in info_names:
                        #print(f"{name} 不在 id 为 {info_id}的数据 {info_names} 中")
                        #print(info_names)
                        index =  info_names.index(name)
                        #print(f"{name}在 id 为 {info_id}的数据 {info_names} 中所在位置为 {index}")
                        wd_glsyj_xq_num = stringToJson(info_record['wd_glsyj_xq_num'])
                        #print(wd_glsyj_xq_num[index])
                        wd_glsyj_xq_num[index] = int(wd_glsyj_xq_num[index]) + 1
                        #print(wd_glsyj_xq_num)
                        
                        update_sql = f"""
                                        UPDATE info_temp 
                                        set
                                        wd_glsyj_xq_num = '{jsonToString(wd_glsyj_xq_num)}',
                                        people_num = people_num +1
                                        where id = {info_id}; 
                                        """
                        #print(update_sql)           
                        tb_ecyj.execute_update(update_sql)              
                        #print(f"不合并:  {id}  存在 info记录 id为{info_id}的 {info_ids}数据中 ,计数+1")
                    else:
                        update_sql = f"""
                                        UPDATE info_temp 
                                        SET type = 'yqdc', 
                                        names = '{jsonToString(names)}', 
                                        car_nos = '{jsonToString(names)}',
                                        wd_glsyj_xq_ids = '{jsonToString(wd_glsyj_xq_ids)}',
                                        wd_glsyj_xq_num = json_array_append(wd_glsyj_xq_num, '$',{1}),
                                        people_num = people_num + 1,
                                        times=NOW(),
                                        update_time = NOW()
                                        WHERE id = {info_id};
                                        """
                        tb_ecyj.execute_update(update_sql)
                    # print(f"合并成功：info_temp记录 {info_record['id']},sql: {update_sql}")
                    continue
                    
                #判断当前id 记录 names 的人数 是否达到阈值，是 将该记录插入到 info 表中 
                #print('=== 人数阈值 ===', self.p_num)
                if people_num >= self.p_num:                 
                    print(f"达到阈值: info_temp id为 {info_id}")
                    #print(people_num >= self.p_num)
                    cx_sql = tb_ecyj.execute_query(f"select * from info where id ={info_id}")
                    
                    #print(len(cx_sql))
                    
                    if len(cx_sql)==0:
                        #print(info_id not in cx_sql)                
                        #获取info_temp中id为{info_id}的记录写入info表                
                        inster_sql = f"""
                                        INSERT INTO info (id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names) 
                                        (SELECT id,type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names FROM info_temp WHERE id = {info_id})
                                        """
                        tb_ecyj.execute_update(inster_sql)
                        print(f"插入成功: info_temp id为 {info_id} 出现{people_num}次")
                    else: #已经存在
                        #更新info中存在的info_temp记录
                        # 如果info表中有唯一键约束（如id为主键）,直接复制info_temp记录到info表
                        insert_sql = """
                            INSERT INTO info (id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names)
                            SELECT id, type, wd_ecyj_id, codes, times, people_num, dw_num, wd_glsyj_xq_ids, start_time, end_time, wd_glsyj_xq_num, car_nos, names, channel_names
                            FROM info_temp 
                            WHERE id = %s
                            ON DUPLICATE KEY UPDATE
                                type = VALUES(type),
                                wd_ecyj_id = VALUES(wd_ecyj_id),
                                codes = VALUES(codes),
                                times = VALUES(times),
                                people_num = VALUES(people_num),
                                dw_num = VALUES(dw_num),
                                wd_glsyj_xq_ids = VALUES(wd_glsyj_xq_ids),
                                start_time = VALUES(start_time),
                                end_time = VALUES(end_time),
                                wd_glsyj_xq_num = VALUES(wd_glsyj_xq_num),
                                car_nos = VALUES(car_nos),
                                names = VALUES(names),
                                channel_names = VALUES(channel_names)
                        """

                        tb_ecyj.execute_update(insert_sql, (info_id,))
                        
                        print(f"id {info_id}在 info 中已经存在，进行更新") 
                    
                
            else: #不存在
                #print(f"不匹配: hist记录 {id} 的时间 {alarmTimeStr} 不在 info记录中 记录长度 {len(info_temp_records)} ")
                endtime=self.calculate_time_range(alarmTimeStr)
                sql = f"SELECT * FROM info_temp WHERE codes like '%{channel_id}%'  AND start_time like '%{alarmTimeStr}%'  AND type = 'yqdc'  LIMIT 200"
                qc_info_temp_records = tb_ecyj.execute_query(sql)
                if len(qc_info_temp_records) > 0: #存在
                    continue
                else: #不存在
                
                    tb_ecyj.execute_update("INSERT INTO info_temp (type,wd_ecyj_id, codes,times,people_num,dw_num,wd_glsyj_xq_ids,start_time, end_time,wd_glsyj_xq_num,car_nos, names, channel_names) VALUES ( %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)",
                                        (
                                            "yqdc",1,jsonToString([channel_id]),datetime.now(),1,1,jsonToString([idstr]), alarmTimeStr,endtime,jsonToString([1]),jsonToString([name]), jsonToString([name]),jsonToString([channel_name])
                                        )
                    )       
            
                #判断当前id 记录end_time 是否结束         
                #tb_ecyj.execute_update("delete from info_temp where id=%s and type ='yqdc' and end_time <= datetime.now()", (info_id,))
                    
        return "执行成功"
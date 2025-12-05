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

# 创建Flask蓝图，命名为'ecyj'，URL前缀为'/ecyj'，统一管理预警相关接口路由
ecyj = Blueprint('ecyj', __name__, url_prefix='/ecyj')


# 1.创建数据库操作类，继承自MySQLHelper，封装预警相关数据处理逻辑
class ecyj_tb(MySQLHelper):
    def __init__(self):
        """初始化预警数据处理类，调用父类构造方法初始化数据库连接"""
        super().__init__()

    def get_early_warning_config(self):
        """
        获取预警配置参数（原有注释保留）
        从wd_ecyj_yddr表查询预警规则配置，包含次数阈值、人数阈值、时间阈值
        :return: 配置字典 {times: 次数阈值, people_num: 人数阈值, ex_time: 时间阈值}，查询无结果返回None
        """
        sql = "SELECT times, people_num, ex_time FROM wd_ecyj_yddr "
        result = self.execute_query(sql)
        return result[0] if result else None

    def process_hist_data(self):
        """
        处理hist表中的数据，根据规则与info_temp表进行比对和合并（原有注释保留）
        核心流程：
        1. 清理hist表无效数据（name为空）
        2. 查询待处理hist数据和现有info_temp数据
        3. 尝试将hist数据与现有info_temp数据合并（严格时间范围校验）
        4. 处理无法合并的hist数据，按时间窗口+类型规则生成新记录
        5. 标记已处理的hist数据
        :return: 处理结果字典，包含成功状态、处理记录数
        """
        # 删除hist表中name为空或空字符串的无效数据，避免无效数据干扰合并逻辑
        delete_empty_sql = "DELETE FROM hist WHERE name IS NULL OR name = ''"
        self.execute_update(delete_empty_sql)
        
        # 查询有效hist数据：name非空、未处理（processed=0），按捕获时间降序取前100条（控制数据量）
        hist_sql = """
        SELECT id, objtype, channelId, channelName, name, cardNo, capTime 
        FROM hist 
        WHERE name IS NOT NULL AND name != '' AND processed = 0
        ORDER BY capTime DESC
        LIMIT 100
        """
        hist_records = self.execute_query(hist_sql)
        print('=== 待处理hist记录 ===', hist_records)  # 调试日志：打印待处理hist记录
        
        # 无待处理数据时直接返回成功响应
        if not hist_records:
            return {"success": True, "message": "没有需要处理的数据"}
        
        # 查询现有info_temp记录（预警临时表），按ID降序取前100条，用于与hist数据比对合并
        info_temp_sql = "SELECT id, type, codes, names, start_time, end_time FROM info_temp ORDER BY id DESC LIMIT 100"
        info_temp_records = list(self.execute_query(info_temp_sql))
        print('=== 现有info_temp记录 ===', info_temp_records)  # 调试日志：打印现有预警临时记录
        
        # 获取预警配置，无配置时使用默认值（原有逻辑保留）
        config = self.get_early_warning_config()
        if config:
            self.times = config['times']  # 合并次数阈值
            self.ex_time = config['ex_time']  # 有效时间阈值（分钟）
            self.people_num = config['people_num']  # 合并最小人数/车辆数阈值
        else:
            self.times = 30  # 默认次数阈值
            self.ex_time = 10  # 默认有效时间阈值（分钟）
            self.people_num = 2  # 默认最小合并数量（至少2个才触发合并）
        
        # 初始化状态变量：未合并的hist记录、已处理hist记录ID集合（避免重复处理）
        remaining_hist_records = []
        processed_hist_ids = set()
        
        # 遍历每条待处理hist记录，尝试与现有info_temp记录合并
        for hist_record in hist_records:
            merged = False  # 标记当前hist记录是否已合并
            # 按ID倒序遍历info_temp记录，优先合并到最新的预警记录
            for info_record in sorted(info_temp_records, key=lambda x: x['id'], reverse=True):
                # 严格校验合并条件（类型匹配+时间在有效期内+关键信息匹配）
                if self._can_merge_with_info_temp(hist_record, info_record):
                    # 执行合并操作，更新info_temp记录
                    self._merge_hist_with_info_temp(hist_record, info_record)
                    processed_hist_ids.add(hist_record['id'])  # 记录已处理ID
                    merged = True
                    print(f"✅ 合并成功：hist[{hist_record['id']}] → info_temp[{info_record['id']}]")
                    break  # 合并成功则跳出当前info_temp遍历
        
            # 未合并的记录加入剩余列表，后续单独处理
            if not merged:
                remaining_hist_records.append(hist_record)
                print(f"❌ 未合并：hist[{hist_record['id']}]，后续将处理为新记录")
        
        print(f'=== 剩余待处理记录数：{len(remaining_hist_records)} ===')
        
        # 处理无法合并的剩余记录，生成新的info_temp预警记录（强化时间窗口判断）
        if remaining_hist_records:
            self._process_remaining_records(remaining_hist_records)
            # 标记剩余记录为已处理
            for record in remaining_hist_records:
                processed_hist_ids.add(record['id'])
        
        # 批量更新已处理的hist记录，设置processed=1（避免重复处理）
        if processed_hist_ids:
            print(f'=== 标记{len(processed_hist_ids)}条记录为已处理 ===')
            # 构造批量更新SQL，使用占位符防止SQL注入
            update_processed_sql = "UPDATE hist SET processed = 1 WHERE id IN ({})".format(
                ','.join(['%s'] * len(processed_hist_ids))
            )
            # 执行更新，参数为整数类型的ID元组（适配数据库字段类型）
            self.execute_update(update_processed_sql, tuple([int(id) for id in processed_hist_ids]))
            
        # 返回处理结果：成功状态 + 总处理记录数
        return {"success": True, "processed_count": len(hist_records)}
    
    def _can_merge_with_info_temp(self, hist_record, info_record):
        """
        判断hist记录是否可以与info_temp记录合并（修复：强化时间段判断）
        核心判断条件（缺一不可）：
        1. 时间：hist的capTime严格在info_temp的start_time~end_time之间
        2. 类型：人员/车辆与预警类型匹配（yddr/yrdd对应人员，yqdc/ycdq对应车辆）
        3. 关键信息：摄像头/区域ID 或 人名/车牌号匹配
        :param hist_record: 待合并的单条hist记录
        :param info_record: 目标合并的单条info_temp记录
        :return: bool - 可合并返回True，否则返回False
        """
        # -------------------------- 修复点1：严格时间范围判断 --------------------------
        try:
            # 转换hist记录的捕获时间（capTime）为datetime（兼容字符串/datetime类型）
            if isinstance(hist_record['capTime'], str):
                captime_dt = datetime.strptime(hist_record['capTime'], '%Y-%m-%d %H:%M:%S')
            else:
                captime_dt = hist_record['capTime']

            # 转换info_temp记录的时间范围（start_time/end_time）
            if isinstance(info_record['start_time'], str):
                start_time_dt = datetime.strptime(info_record['start_time'], '%Y-%m-%d %H:%M:%S')
            else:
                start_time_dt = info_record['start_time']
            
            if isinstance(info_record['end_time'], str):
                end_time_dt = datetime.strptime(info_record['end_time'], '%Y-%m-%d %H:%M:%S')
            else:
                end_time_dt = info_record['end_time']
        except Exception as e:
            print(f"⚠️  时间格式转换错误：{e}，hist_id={hist_record['id']}")
            return False

        # 核心校验：hist的capTime必须严格在info_temp的[start_time, end_time]范围内
        if not (start_time_dt <= captime_dt <= end_time_dt):
            print(f"⚠️  时间不在范围内：hist_capTime={captime_dt}，info_time=[{start_time_dt}, {end_time_dt}]")
            return False
        
        # -------------------------- 修复点2：正确解析codes/names（避免列表丢失） --------------------------
        # 解析info_temp的codes和names字段（强制转为列表，容错JSON解析失败）
        try:
            codes = json.loads(info_record['codes']) if isinstance(info_record['codes'], str) else info_record['codes']
            names = json.loads(info_record['names']) if isinstance(info_record['names'], str) else info_record['names']
        except (json.JSONDecodeError, TypeError):
            codes = []
            names = []
        
        # 强制转为列表（避免单值非列表导致的添加失败）
        codes = codes if isinstance(codes, list) else [str(codes)] if codes else []
        names = names if isinstance(names, list) else [str(names)] if names else []
        
        # -------------------------- 基础匹配信息提取 --------------------------
        channel_id = str(hist_record['channelId'])  # 统一转为字符串，避免类型差异
        name = hist_record['name']  # 人名/车牌号
        objtype = hist_record['objtype']  # 目标类型：5=人员，1=车辆
        info_type = info_record['type']  # 预警类型：yddr(一点多人)/yrdd(一人多点)/yqdc(一区多车)/ycdq(一车多区)
        
        print(f"=== 匹配校验 ===")
        print(f"hist: channel_id={channel_id}, name={name}, objtype={objtype}, capTime={captime_dt}")
        print(f"info_temp: type={info_type}, codes={codes}, names={names}, time=[{start_time_dt}, {end_time_dt}]")
        
        # -------------------------- 类型匹配校验 --------------------------
        # 人员记录只能合并到人员相关预警，车辆记录只能合并到车辆相关预警
        is_person_related = (objtype == 5 and info_type in ['yddr', 'yrdd'])
        is_vehicle_related = (objtype == 1 and info_type in ['yqdc', 'ycdq'])
        if not (is_person_related or is_vehicle_related):
            print(f"⚠️  类型不匹配：objtype={objtype} 无法合并到 info_type={info_type}")
            return False
            
        # -------------------------- 关键信息匹配规则 --------------------------
        # 统一转为字符串列表，避免类型不匹配导致的比较错误
        str_codes = [str(code) for code in codes]
        str_names = [str(n) for n in names]
        
        # 按预警类型执行不同的匹配规则
        match_rule = {
            (5, 'yddr'): channel_id in str_codes,    # 一点多人：同摄像头（channelId匹配）
            (5, 'yrdd'): name in str_names,          # 一人多点：同人（name匹配）
            (1, 'yqdc'): channel_id in str_codes,    # 一区多车：同区域（channelId匹配）
            (1, 'ycdq'): name in str_names           # 一车多区：同车（name匹配）
        }
        can_merge = match_rule.get((objtype, info_type), False)
        
        print(f"=== 匹配结果：{can_merge} ===")
        return can_merge

    def _merge_hist_with_info_temp(self, hist_record, info_record):
        """
        将hist记录合并到info_temp记录中（修复：确保codes/names列表正确更新）
        按预警类型更新字段：
        - yddr/yrdd（人员）：更新names/codes + 延长end_time
        - yqdc/ycdq（车辆）：更新names/codes + 延长end_time
        :param hist_record: 待合并的hist记录
        :param info_record: 目标info_temp记录
        """
        print(f"=== 开始合并 ===")
        # 提取合并所需关键信息
        channel_id = str(hist_record['channelId'])
        name = hist_record['name']
        objtype = hist_record['objtype']  # 5=人员，1=车辆
        info_type = info_record['type']  # 预警类型
        captime = hist_record['capTime']
        captime_dt = datetime.strptime(str(captime), '%Y-%m-%d %H:%M:%S')
        
        # -------------------------- 修复点：重新查询最新的codes/names（避免脏数据） --------------------------
        # 合并前重新查询info_temp的最新数据，防止并发更新导致的字段不一致
        select_sql = "SELECT codes, names FROM info_temp WHERE id = %s"
        info_latest = self.execute_query(select_sql, (info_record['id'],))[0]
        
        # 解析并强制转为列表
        codes = json.loads(info_latest['codes']) if isinstance(info_latest['codes'], str) else info_latest['codes']
        names = json.loads(info_latest['names']) if isinstance(info_latest['names'], str) else info_latest['names']
        codes = codes if isinstance(codes, list) else [str(codes)] if codes else []
        names = names if isinstance(names, list) else [str(names)] if names else []
        
        # 统一转为字符串，避免类型差异
        codes = [str(code) for code in codes]
        names = [str(name) for name in names]
        
        print(f"info_temp最新数据：codes={codes}, names={names}")
        
        # -------------------------- 按类型执行合并逻辑 --------------------------
        update_data = {}
        if objtype == 5:  # 人员相关记录合并
            if info_type == 'yddr':
                # 一点多人：添加新人名（去重）
                if name not in names:
                    names.append(name)
                update_data['names'] = json.dumps(names)
            elif info_type == 'yrdd':
                # 一人多点：添加新摄像头ID（去重）- 修复codes只显示一个的问题
                if channel_id not in codes:
                    codes.append(channel_id)
                update_data['codes'] = json.dumps(codes)
        elif objtype == 1:  # 车辆相关记录合并
            if info_type == 'yqdc':
                # 一区多车：添加新车牌号（去重）- 修复yqdc未合并的问题
                if name not in names:
                    names.append(name)
                update_data['names'] = json.dumps(names)
            elif info_type == 'ycdq':
                # 一车多区：添加新区域ID（去重）- 修复codes只显示一个的问题
                if channel_id not in codes:
                    codes.append(channel_id)
                update_data['codes'] = json.dumps(codes)
        
        # -------------------------- 延长有效结束时间 --------------------------
        # 新end_time = 最新捕获时间 + 配置阈值（确保后续同类型记录可合并）
        new_end_time = captime_dt + timedelta(minutes=self.times + self.ex_time)
        update_data['end_time'] = new_end_time.strftime('%Y-%m-%d %H:%M:%S')
        update_data['update_time'] = 'NOW()'
        
        # -------------------------- 执行更新 --------------------------
        update_sql = f"""
        UPDATE info_temp 
        SET {', '.join([f'{k} = %s' for k in update_data.keys() if k != 'update_time'])}
            , update_time = NOW()
        WHERE id = %s
        """
        # 构造参数（排除update_time，直接用NOW()函数）
        params = [v for k, v in update_data.items() if k != 'update_time'] + [info_record['id']]
        self.execute_update(update_sql, tuple(params))
        
        print(f"=== 合并完成：info_temp[{info_record['id']}] 更新为 {update_data} ===")

    def _process_remaining_records(self, remaining_hist_records):
        """
        处理无法与现有记录合并的剩余记录（修复：yqdc合并逻辑 + 时间窗口筛选）
        核心改进：
        1. 组内记录必须在同一时间窗口内（第一条记录时间+配置阈值）
        2. 正确识别yqdc组（同channelId+不同车辆name）
        3. 避免车辆记录全部转为ycdq
        :param remaining_hist_records: 未合并的hist记录列表
        """
        print(f"=== 处理剩余{len(remaining_hist_records)}条记录 ===")
        
        # -------------------------- 预分组：按channelId和name分组 --------------------------
        records_by_channel = {}  # key: channelId（字符串）, value: 该channel下的记录列表
        records_by_name = {}     # key: name（字符串）, value: 该name下的记录列表
        
        for record in remaining_hist_records:
            channel_id = str(record['channelId'])
            name = str(record['name'])
            objtype = record['objtype']
            
            # 按channelId分组（用于yddr/yqdc识别）
            if channel_id not in records_by_channel:
                records_by_channel[channel_id] = []
            records_by_channel[channel_id].append(record)
            
            # 按name分组（用于yrdd/ycdq识别）
            if name not in records_by_name:
                records_by_name[name] = []
            records_by_name[name].append(record)
        
        # 按捕获时间升序排序，便于时间窗口判断
        for channel in records_by_channel:
            records_by_channel[channel].sort(key=lambda x: x['capTime'])
        for name in records_by_name:
            records_by_name[name].sort(key=lambda x: x['capTime'])
        
        # -------------------------- 初始化变量 --------------------------
        processed_ids = set()  # 已处理记录ID，避免重复
        groups = {
            'yddr': [],  # 一点多人（人员+同channel+不同name+同时间窗口）
            'yrdd': [],  # 一人多点（人员+同name+不同channel+同时间窗口）
            'yqdc': [],  # 一区多车（车辆+同channel+不同name+同时间窗口）
            'ycdq': []   # 一车多区（车辆+同name+不同channel+同时间窗口）
        }
        
        # -------------------------- 1. 识别yddr组（一点多人） --------------------------
        for channel_id, records in records_by_channel.items():
            person_records = [r for r in records if r['objtype'] == 5]
            if len(person_records) < self.people_num:
                continue  # 未达到最小人数阈值，跳过
            
            # 按时间窗口分组：同一窗口内的记录才合并
            current_window_records = []
            for record in person_records:
                if not current_window_records:
                    # 第一个记录作为窗口起始
                    current_window_records.append(record)
                    window_start = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    window_end = window_start + timedelta(minutes=self.times + self.ex_time)
                else:
                    # 后续记录需在当前窗口内
                    record_time = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    if record_time <= window_end:
                        current_window_records.append(record)
                    else:
                        # 超出窗口，结算当前组
                        if len(set(r['name'] for r in current_window_records)) >= self.people_num:
                            groups['yddr'].append(current_window_records)
                            for r in current_window_records:
                                processed_ids.add(r['id'])
                        # 开启新窗口
                        current_window_records = [record]
                        window_start = record_time
                        window_end = window_start + timedelta(minutes=self.times + self.ex_time)
            
            # 结算最后一个窗口
            if current_window_records and len(set(r['name'] for r in current_window_records)) >= self.people_num:
                groups['yddr'].append(current_window_records)
                for r in current_window_records:
                    processed_ids.add(r['id'])
        
        # -------------------------- 2. 识别yrdd组（一人多点） --------------------------
        for name, records in records_by_name.items():
            person_records = [r for r in records if r['objtype'] == 5]
            if len(person_records) < self.people_num:
                continue
            
            current_window_records = []
            for record in person_records:
                if not current_window_records:
                    current_window_records.append(record)
                    window_start = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    window_end = window_start + timedelta(minutes=self.times + self.ex_time)
                else:
                    record_time = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    if record_time <= window_end:
                        current_window_records.append(record)
                    else:
                        # 结算当前组（不同channel数量达标）
                        if len(set(str(r['channelId']) for r in current_window_records)) >= self.people_num:
                            groups['yrdd'].append(current_window_records)
                            for r in current_window_records:
                                processed_ids.add(r['id'])
                        # 新窗口
                        current_window_records = [record]
                        window_start = record_time
                        window_end = window_start + timedelta(minutes=self.times + self.ex_time)
            
            # 结算最后一个窗口
            if current_window_records and len(set(str(r['channelId']) for r in current_window_records)) >= self.people_num:
                groups['yrdd'].append(current_window_records)
                for r in current_window_records:
                    processed_ids.add(r['id'])
        
        # -------------------------- 3. 识别yqdc组（一区多车）- 修复未合并问题 --------------------------
        for channel_id, records in records_by_channel.items():
            vehicle_records = [r for r in records if r['objtype'] == 1]
            if len(vehicle_records) < self.people_num:
                continue
            
            current_window_records = []
            for record in vehicle_records:
                if not current_window_records:
                    current_window_records.append(record)
                    window_start = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    window_end = window_start + timedelta(minutes=self.times + self.ex_time)
                else:
                    record_time = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    if record_time <= window_end:
                        current_window_records.append(record)
                    else:
                        # 结算当前组（不同车牌号数量达标）
                        if len(set(r['name'] for r in current_window_records)) >= self.people_num:
                            groups['yqdc'].append(current_window_records)
                            for r in current_window_records:
                                processed_ids.add(r['id'])
                        # 新窗口
                        current_window_records = [record]
                        window_start = record_time
                        window_end = window_start + timedelta(minutes=self.times + self.ex_time)
            
            # 结算最后一个窗口
            if current_window_records and len(set(r['name'] for r in current_window_records)) >= self.people_num:
                groups['yqdc'].append(current_window_records)
                for r in current_window_records:
                    processed_ids.add(r['id'])
        
        # -------------------------- 4. 识别ycdq组（一车多区） --------------------------
        for name, records in records_by_name.items():
            vehicle_records = [r for r in records if r['objtype'] == 1]
            if len(vehicle_records) < self.people_num:
                continue
            
            current_window_records = []
            for record in vehicle_records:
                if not current_window_records:
                    current_window_records.append(record)
                    window_start = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    window_end = window_start + timedelta(minutes=self.times + self.ex_time)
                else:
                    record_time = datetime.strptime(str(record['capTime']), '%Y-%m-%d %H:%M:%S')
                    if record_time <= window_end:
                        current_window_records.append(record)
                    else:
                        # 结算当前组（不同区域数量达标）
                        if len(set(str(r['channelId']) for r in current_window_records)) >= self.people_num:
                            groups['ycdq'].append(current_window_records)
                            for r in current_window_records:
                                processed_ids.add(r['id'])
                        # 新窗口
                        current_window_records = [record]
                        window_start = record_time
                        window_end = window_start + timedelta(minutes=self.times + self.ex_time)
            
            # 结算最后一个窗口
            if current_window_records and len(set(str(r['channelId']) for r in current_window_records)) >= self.people_num:
                groups['ycdq'].append(current_window_records)
                for r in current_window_records:
                    processed_ids.add(r['id'])
        
        # -------------------------- 打印分组结果 --------------------------
        print(f"=== 分组结果 ===")
        for group_type, group_list in groups.items():
            print(f"{group_type}: {len(group_list)}组")
            for idx, group in enumerate(group_list):
                print(f"  组{idx+1}：{[r['id'] for r in group]}")
        
        # -------------------------- 为各分组创建预警记录 --------------------------
        for group_type, group_list in groups.items():
            for group in group_list:
                if group_type == 'yddr':
                    self._create_yddr_record(group)
                elif group_type == 'yrdd':
                    self._create_yrdd_record(group)
                elif group_type == 'yqdc':
                    self._create_yqdc_record(group)
                elif group_type == 'ycdq':
                    self._create_ycdq_record(group)
        
        # -------------------------- 处理未分组记录（单条记录） --------------------------
        ungrouped_records = [r for r in remaining_hist_records if r['id'] not in processed_ids]
        print(f"=== 未分组记录（单条创建）：{[r['id'] for r in ungrouped_records]} ===")
        for record in ungrouped_records:
            self._create_single_record(record)

    def _create_yddr_record(self, group):
        """创建一点多人(yddr)记录（修复：确保codes/names正确）"""
        base_record = group[0]
        base_time = datetime.strptime(str(base_record['capTime']), '%Y-%m-%d %H:%M:%S')
        end_time = base_time + timedelta(minutes=self.times + self.ex_time)
        
        # codes：当前摄像头ID（单个，字符串类型）
        codes = [str(base_record['channelId'])]
        # names：组内所有不同人名（去重）
        names = list(set(str(r['name']) for r in group))
        
        insert_sql = """
        INSERT INTO info_temp 
        (type, codes, names, start_time, end_time, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.execute_update(insert_sql, (
            "yddr",
            json.dumps(codes),
            json.dumps(names),
            base_record['capTime'],
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        print(f"✅ 创建yddr记录：codes={codes}, names={names}")

    def _create_yrdd_record(self, group):
        """创建一人多点(yrdd)记录（修复：codes显示多个摄像头ID）"""
        base_record = group[0]
        base_time = datetime.strptime(str(base_record['capTime']), '%Y-%m-%d %H:%M:%S')
        end_time = base_time + timedelta(minutes=self.times + self.ex_time)
        
        # codes：组内所有不同摄像头ID（去重，字符串类型）- 修复只显示一个的问题
        codes = list(set(str(r['channelId']) for r in group))
        # names：当前人名（单个）
        names = [str(base_record['name'])]
        
        insert_sql = """
        INSERT INTO info_temp 
        (type, codes, names, start_time, end_time, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.execute_update(insert_sql, (
            "yrdd",
            json.dumps(codes),
            json.dumps(names),
            base_record['capTime'],
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        print(f"✅ 创建yrdd记录：codes={codes}, names={names}")

    def _create_yqdc_record(self, group):
        """创建一区多车(yqdc)记录（修复：正确合并同区域多车辆）"""
        base_record = group[0]
        base_time = datetime.strptime(str(base_record['capTime']), '%Y-%m-%d %H:%M:%S')
        end_time = base_time + timedelta(minutes=self.times + self.ex_time)
        
        # codes：当前区域ID（单个，字符串类型）
        codes = [str(base_record['channelId'])]
        # names：组内所有不同车牌号（去重）
        names = list(set(str(r['name']) for r in group))
        
        insert_sql = """
        INSERT INTO info_temp 
        (type, codes, names, start_time, end_time, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.execute_update(insert_sql, (
            "yqdc",
            json.dumps(codes),
            json.dumps(names),
            base_record['capTime'],
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        print(f"✅ 创建yqdc记录：codes={codes}, names={names}")

    def _create_ycdq_record(self, group):
        """创建一车多区(ycdq)记录（修复：codes显示多个区域ID）"""
        base_record = group[0]
        base_time = datetime.strptime(str(base_record['capTime']), '%Y-%m-%d %H:%M:%S')
        end_time = base_time + timedelta(minutes=self.times + self.ex_time)
        
        # codes：组内所有不同区域ID（去重，字符串类型）- 修复只显示一个的问题
        codes = list(set(str(r['channelId']) for r in group))
        # names：当前车牌号（单个）
        names = [str(base_record['name'])]
        
        insert_sql = """
        INSERT INTO info_temp 
        (type, codes, names, start_time, end_time, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.execute_update(insert_sql, (
            "ycdq",
            json.dumps(codes),
            json.dumps(names),
            base_record['capTime'],
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        print(f"✅ 创建ycdq记录：codes={codes}, names={names}")
        
    def _create_single_record(self, record):
        """
        创建单条记录（修复：车辆单条记录默认yqdc，而非ycdq）
        单条记录类型规则：
        - 人员（objtype=5）：yrdd（一人单点）
        - 车辆（objtype=1）：yqdc（一区单车）
        """
        captime = record['capTime']
        captime_dt = datetime.strptime(str(captime), '%Y-%m-%d %H:%M:%S')
        end_time = captime_dt + timedelta(minutes=self.times + self.ex_time)
        objtype = record['objtype']
        
        # 修复：车辆单条记录默认yqdc，避免全部显示为ycdq
        record_type = "yrdd" if objtype == 5 else "yqdc"
        codes = [str(record['channelId'])]  # 单个摄像头/区域ID
        names = [str(record['name'])]       # 单个人名/车牌号
        
        insert_sql = """
        INSERT INTO info_temp 
        (type, codes, names, start_time, end_time, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.execute_update(insert_sql, (
            record_type,
            json.dumps(codes),
            json.dumps(names),
            captime,
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        print(f"✅ 创建单条{record_type}记录：codes={codes}, names={names}")


# 实例化预警数据处理类，供接口调用
c_ecyj = ecyj_tb()

@ecyj.route('/process_hist_data', methods=['GET'])
def process_hist_data():
    """
    处理hist表数据的API接口（原有注释保留）
    对外提供GET请求接口，触发hist数据与info_temp的合并处理逻辑
    :return: JSON响应 - 处理成功返回结果，失败返回错误信息和500状态码
    """
    try:
        # 调用数据处理核心方法
        result = c_ecyj.process_hist_data()
        return jsonify(result)  # 返回成功响应
    except Exception as e:
        # 捕获异常，返回错误信息和500服务器错误状态码
        print(f"❌ 接口处理异常：{str(e)}")
        return jsonify({"error": str(e)}), 500
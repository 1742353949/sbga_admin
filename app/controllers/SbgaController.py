from app.helper.helper import *
from app.models.base_db import MySQLHelper  # 导入 MySQLHelper
from flask import request  # 添加 request 导入
from datetime import datetime
import json
# 导入wd_ybss_ry表
from app.models.SBGA.Sbga_tb import sbga_tb

#创建实例
tb=sbga_tb()
class SbgaController():
    def __init__(self)->None:
        super().__init__()
        self.__tbname = "wd_ybss_ry"
        
    def get_wdybss_by_id(self,id):
        #获取用户信息
        data= tb.get_wd_ybss_by_id(id)
        return data
    
    def get_wdybss_count(self):
        #获取总人数信息
        data= tb.get_wd_ybss_count()
        # 提取计数结果
        if data and len(data) > 0:
            count = list(data[0].values())[0]
            return {"total_count": count}
        return {"total_count": 0}
    
    def get_wd_ybss_sex_count(self,sex):
        #获取性别信息
        data= tb.get_wd_ybss_sex_count(sex)
        # 提取计数结果
        if data and len(data) > 0:
            count = list(data[0].values())[0]
            return {"sex": sex, "count": count}
        return {"sex": sex, "count": 0}
        
    def get_wd_ybss_all_sex_count(self):
        # 获取所有性别统计数据
        data = tb.get_wd_ybss_all_sex_count()
        return {"sex_statistics": data}
        
    def get_wd_ybss_list(self, page=1, page_size=100):
        """
        分页获取人员列表
        :param page: 页码，默认为1
        :param page_size: 每页条数，默认为100
        :return: 人员列表
        """
        data = tb.get_wd_ybss_list(page, page_size)
        return {"page": page, "page_size": page_size, "data": data}
        
    def get_wd_ybss_list_by_sex(self, sex, page=1, page_size=100):
        """
        根据性别分页获取人员列表
        :param sex: 性别
        :param page: 页码，默认为1
        :param page_size: 每页条数，默认为100
        :return: 人员列表
        """
        condition = "sex = %s"
        params = [sex]
        data = tb.get_wd_ybss_list_by_condition(condition, params, page, page_size)
        return {"sex": sex, "page": page, "page_size": page_size, "data": data}
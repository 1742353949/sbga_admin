from app.helper.helper import *
from app.models.BS_MG.Planting_db import PlantingDb
from app.models.BS_MG.grid_db import GridDb
from app.models.base_db import MySQLHelper  # 导入 MySQLHelper
from flask import request  # 添加 request 导入

plantingdb = PlantingDb()
griddb = GridDb()

class GridController():
    def __init__(self) -> None:
        super().__init__()
        self.__tbname = "fdkj_bs_mg_planting"

    def getAllInfo(self):
        ptb = plantingdb._tbname
        gtb = griddb._tbname
        sql = f"""SELECT a.*,
        COALESCE(SUM(b.SMAREA)*0.0015, 0) AS sj_area,
        a.area - COALESCE(SUM(b.SMAREA) * 0.0015, 0) AS c_area,
	    COALESCE(SUM(b.SMAREA)*0.0015 * 1200, 0) sj_num
        FROM {ptb} AS a
        LEFT JOIN {gtb} AS b 
        ON a.name = b.username
        GROUP BY a.id;""" 
        data = griddb.execute_query(sql)
        return echo_json(True,'success',data)


    
    def getPlantingInfo(self,name):  # 添加 self 参数
        try:
            data = {"name":"zzy"}
            data = plantingdb.get_user_info_by_name(name)
            other = plantingdb.get_table_columns_and_comments()
            print(data)
            return echo_json(True,'success',data,other)
        except Exception as e:
            print(f"获取种植信息失败: {e}")
            return echo_json(False, 'failure', None)

    def test_database_connection(self):
        """测试数据库连接"""
        try:
            mysql_helper = MySQLHelper()
            mysql_helper.connect()
            real_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            print(f"客户端 IP 地址: {real_ip}")
            if mysql_helper.connection:
                print("数据库连接成功")
            else:
                print("数据库连接失败，请检查配置文件中的用户名和密码是否正确")
        except Exception as e:
            print(f"测试数据库连接失败: {e}")
            print(f"详细错误信息: {e.args}")
            # 获取客户端的真实 IP 地址
            real_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            print(f"客户端 IP 地址: {real_ip}")

        return echo_json(False, 'failure', None)

from app.models.base_db import MySQLHelper

class PlantingDb(MySQLHelper):
    def __init__(self):
        super().__init__()
        self._tbname = 'fdkj_bs_mg_planting'

    def get_user_info_by_id(self,id):
        sql = f"select * from {self._tbname} where id = %s"
        return self.execute_query(sql, (id))
    
    def get_user_info_by_name(self,name):
        sql = f"select * from {self._tbname} where name = %s"
        return self.execute_query(sql, (name))
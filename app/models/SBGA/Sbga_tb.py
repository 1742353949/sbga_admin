from app.models.base_db import MySQLHelper
class sbga_tb(MySQLHelper):
    def __init__(self):
        super().__init__()
        self._tbname="wd_ybss_ry"
    
    #查询用户信息通过id值
    def get_wd_ybss_by_id(self,id):
        sql=f"select * from {self._tbname} where id=%s"
        return self.execute_query(sql,(id))
    
    #查询总人数
    def get_wd_ybss_count(self):
        sql=f"select count(*) from {self._tbname}"
        return self.execute_query(sql)
    #查询性别人数
    def get_wd_ybss_sex_count(self,sex):
        sql=f"select count(*) from {self._tbname} where sex=%s"
        return self.execute_query(sql,(sex))
        
    #查询男女分别统计人数
    def get_wd_ybss_all_sex_count(self):
        sql = f"select sex, count(*) as count from {self._tbname} group by sex"
        return self.execute_query(sql)
        
    #分页查询所有人员信息
    def get_wd_ybss_list(self, page=1, page_size=100):
        offset = (page - 1) * page_size
        sql = f"select * from {self._tbname} limit %s offset %s"
        return self.execute_query(sql, (page_size, offset))
        
    #查询所有人员信息（带条件）
    def get_wd_ybss_list_by_condition(self, condition=None, params=None, page=1, page_size=100):
        offset = (page - 1) * page_size
        if condition:
            sql = f"select * from {self._tbname} where {condition} limit %s offset %s"
            params = params or []
            params.extend([page_size, offset])
        else:
            sql = f"select * from {self._tbname} limit %s offset %s"
            params = [page_size, offset]
        return self.execute_query(sql, params)
from app.models.base_db import MySQLHelper

class CommonDB(MySQLHelper):
    def __init__(self):
        super().__init__()

    def sqlQuery(self,query):
         return self.execute_query(query)
    
    def sqlUpdate(self,query):
         return self.execute_update(query)

import pymysql
from pymysql.cursors import DictCursor
from flask import current_app
from config import MysqlConfig

# class MySQLHelper:
#     def __init__(self, database=None):
#         self.host =  MysqlConfig.HOST
#         self.user =  MysqlConfig.USER
#         self.password = MysqlConfig.PASSWORD
#         if database is None:
#             self.database = MysqlConfig.DB
#         else:
#             self.database = database
#         self.conn = None
#         self.connection = None
#         self._tbname = None

#     def connect(self):
#         """建立数据库连接"""
#         if self.connection is None:
#             try:
#                 self.connection = pymysql.connect(
#                     host= MysqlConfig.HOST,
#                     user= MysqlConfig.USER,
#                     password=MysqlConfig.PASSWORD,
#                     database=self.database,
#                     cursorclass=DictCursor
#                 )
#             except Exception as e:
#                 print(f"数据库连接失败: {e}")
#                 print("host:", MysqlConfig.HOST)
#         # return self.conn

#     def execute_query(self, query, params=None):
#         """执行查询语句"""
#         if self.connection is None:
#             self.connect()
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(query, params)
#                 result = cursor.fetchall()
#             return result
#         except Exception as e:
#             print(f"查询执行失败: {e}")
#             return f"查询执行失败: {e}"
#             # self.connect()
#             # return self.execute_query(query, params)

#     def execute_update(self, query, params=None):
#         """执行更新语句"""
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(query, params)
#             self.connection.commit()
#             return cursor.rowcount
#         except Exception as e:
#             self.connection.rollback()
#             print(f"更新执行失败: {e}")
#             return f"更新执行失败: {e}"

#     def close(self):
#         """关闭数据库连接"""
#         if self.connection:
#             self.connection.close()
#             self.connection = None

from DBUtils.PooledDB import PooledDB

class MySQLHelper:
    def __init__(self, database=None):
        print(MysqlConfig.HOST)
        self.pool = PooledDB(
            creator=pymysql,
            host=MysqlConfig.HOST,
            user=MysqlConfig.USER,
            password=MysqlConfig.PASSWORD,
            database=database or MysqlConfig.DB,
            cursorclass=DictCursor,
            maxconnections=5,
            blocking=True,
            ping=0
        )

    def get_connection(self):
        return self.pool.connection()

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            conn.close()

    def execute_update(self, query, params=None):
        """执行插入、更新、删除操作"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                result = cursor.execute(query, params)
            conn.commit()  # 提交事务
            return result  # 返回受影响的行数
        except Exception as e:
            conn.rollback()  # 出错回滚
            print(f"执行写操作失败: {e}")
            return 0
        finally:
            conn.close()

    def get_table_columns_and_comments(self):
        """查询表字段和注释"""
        try:
            query = """
            SELECT 
                COLUMN_NAME, 
                COLUMN_COMMENT
            FROM 
                information_schema.columns
            WHERE 
                TABLE_SCHEMA = %s 
                AND TABLE_NAME = %s;
            """
            # 使用 get_connection 方法获取连接
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, (self.database, self._tbname))
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception as e:
            print(f"获取字段信息失败: {e}")
            return None  

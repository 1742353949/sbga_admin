from flask import Flask
import pymysql

app = Flask(__name__)

# MySQL数据库连接配置

db_config = {
    'host': '132.232.137.173',
    # 'host': '127.0.0.1',
    'user': 'kmlskj',
    'password': 'kmlskj@123',
    'database': 'fd_wd_ga_data',
    'charset': 'utf8mb4',
    "connect_timeout":30,  # 默认是10秒，这里增加到30秒
    "read_timeout":30,     # 读取操作超时
    "write_timeout":30     # 写入操作超时
}

@app.route('/')
def index():
    try:
        # 使用 PyMySQL 连接数据库
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            data = cursor.fetchone()
        connection.close()
        return f"MySQL 版本: {data[0]}"
    except Exception as e:
        return f"数据库查询出错: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
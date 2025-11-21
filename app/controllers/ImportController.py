import pandas as pd
import json
from flask import jsonify, request
from app.models.base_db import MySQLHelper
import os
import uuid
import time
from werkzeug.utils import secure_filename
import numpy as np

# 尝试导入openpyxl，如果不存在则在需要时给出友好的错误提示
try:
    import openpyxl
    HAS_OPENPYXL = True
    OPENPYXL_ERROR = None
except ImportError as e:
    HAS_OPENPYXL = False
    OPENPYXL_ERROR = str(e)


class ImportController:
    """
    通用表格导入控制器
    支持Excel、CSV等格式文件导入到数据库中
    """

    def __init__(self):
        """
        初始化控制器
        """
        self.db = MySQLHelper()
        # 设置上传目录
        self.upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'import')
        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)

    def get_tables(self):
        """
        获取数据库中所有表名
        
        Returns:
            dict: 包含所有表名的字典
        """
        try:
            # 查询所有表名
            query = "SHOW TABLES"
            result = self.db.execute_query(query)
            
            # 获取表名列表
            tables = []
            for row in result:
                # MySQL返回的结果键名为Tables_in_{数据库名}
                table_name = list(row.values())[0]
                # 处理可能的字节字符串
                if isinstance(table_name, (bytes, bytearray)):
                    table_name = table_name.decode('utf-8')
                # 确保是字符串类型
                table_name = str(table_name)
                tables.append(table_name)
                
            return {"code": 200, "msg": "获取成功", "data": tables}
        except Exception as e:
            return {"code": 500, "msg": f"获取表列表失败: {str(e)}"}

    def get_table_structure(self, table_name):
        """
        获取指定表的结构信息
        
        Args:
            table_name (str): 表名
            
        Returns:
            dict: 包含表结构信息的字典
        """
        try:
            print(f"开始获取表结构，表名: {table_name}")
            
            # 获取表字段信息
            columns_info = self.db.get_table_columns_and_comments(table_name)
            print(f"从数据库获取的columns_info: {columns_info}")
            
            # 处理列名中的可能字节字符串
            if columns_info:
                print("处理列名中的字节字符串")
                for col in columns_info:
                    print(f"处理列: {col}")
                    for key in col:
                        if isinstance(col[key], (bytes, bytearray)):
                            col[key] = col[key].decode('utf-8')
                            print(f"解码字节字符串 {key}: {col[key]}")
                        # 确保是字符串类型
                        col[key] = str(col[key])
                        print(f"转换为字符串 {key}: {col[key]}")
            else:
                # 如果没有获取到字段信息，则初始化为空列表
                print("columns_info为空，初始化为空列表")
                columns_info = []
            
            print(f"处理后的columns_info: {columns_info}")
            
            # 获取表的创建语句以了解字段类型
            create_query = f"SHOW CREATE TABLE `{table_name}`"
            print(f"执行创建语句查询: {create_query}")
            create_result = self.db.execute_query(create_query)
            print(f"创建语句查询结果: {create_result}")
            create_sql = create_result[0]['Create Table'] if create_result else ""
            print(f"提取的Create Table: {create_sql}")
            
            # 处理可能的字节字符串
            if isinstance(create_sql, (bytes, bytearray)):
                create_sql = create_sql.decode('utf-8')
                print(f"解码创建语句字节字符串: {create_sql}")
            # 确保是字符串类型
            create_sql = str(create_sql)
            print(f"最终创建语句: {create_sql}")
            
            result = {
                "code": 200, 
                "msg": "获取成功", 
                "data": {
                    "columns": columns_info,
                    "create_sql": create_sql
                }
            }
            print(f"返回结果: {result}")
            return result
        except Exception as e:
            print(f"获取表结构失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"code": 500, "msg": f"获取表结构失败: {str(e)}"}

    def _convert_numpy_types(self, obj):
        """
        转换numpy类型为Python原生类型，确保JSON序列化正确
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (bytes, bytearray)):
            return obj.decode('utf-8')
        elif pd.isna(obj):  # 处理pandas的NaN值
            return None
        return obj

    def preview_file_data(self, file_path, file_type='excel'):
        """
        预览上传文件的数据
        
        Args:
            file_path (str): 文件路径
            file_type (str): 文件类型 ('excel', 'csv')
            
        Returns:
            dict: 包含文件预览数据的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"code": 400, "msg": "文件不存在"}
            
            # 根据文件类型读取数据
            if file_type.lower() == 'excel':
                # 检查openpyxl是否可用
                if not HAS_OPENPYXL:
                    return {"code": 500, "msg": "缺少必要的依赖库: openpyxl未安装。请使用pip install openpyxl安装openpyxl库以支持Excel文件。"}
                
                try:
                    df = pd.read_excel(file_path, nrows=10)  # 只读取前10行作为预览
                except Exception as e:
                    return {"code": 500, "msg": f"读取Excel文件失败: {str(e)}"}
            elif file_type.lower() == 'csv':
                # 读取CSV文件
                try:
                    df = pd.read_csv(file_path, nrows=10)  # 只读取前10行作为预览
                except Exception as e:
                    return {"code": 500, "msg": f"读取CSV文件失败: {str(e)}"}
            else:
                return {"code": 400, "msg": "不支持的文件类型"}
            
            # 处理NaN值，将其替换为None以便JSON序列化
            df = df.where(pd.notnull(df), None)
            
            # 将DataFrame转换为字典列表
            data_preview = df.to_dict('records')
            columns = df.columns.tolist()
            
            # 确保列名也正确处理，避免Unicode转义
            processed_columns = []
            for col in columns:
                if isinstance(col, (bytes, bytearray)):
                    col = col.decode('utf-8')
                # 确保是字符串类型
                col = str(col)
                processed_columns.append(col)
            
            # 确保数据中的字符串正确处理Unicode字符
            processed_preview = []
            for row in data_preview:
                processed_row = {}
                for key, value in row.items():
                    # 处理键
                    processed_key = key
                    if isinstance(key, (bytes, bytearray)):
                        processed_key = key.decode('utf-8')
                    # 确保是字符串类型
                    processed_key = str(processed_key)
                    
                    # 处理值
                    processed_value = self._convert_numpy_types(value)
                    
                    processed_row[processed_key] = processed_value
                processed_preview.append(processed_row)
            
            return {
                "code": 200,
                "msg": "预览成功",
                "data": {
                    "columns": processed_columns,
                    "preview_data": processed_preview,
                    "total_rows": len(df)
                }
            }
        except Exception as e:
            return {"code": 500, "msg": f"文件预览失败: {str(e)}"}

    def import_data(self, file_path, table_name, mapping_config, file_type='excel'):
        """
        将文件数据导入到数据库
        
        Args:
            file_path (str): 文件路径
            table_name (str): 目标表名
            mapping_config (dict): 字段映射配置
            file_type (str): 文件类型 ('excel', 'csv')
            
        Returns:
            dict: 导入结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"code": 400, "msg": "文件不存在"}
            
            # 读取完整文件数据
            if file_type.lower() == 'excel':
                # 检查openpyxl是否可用
                if not HAS_OPENPYXL:
                    return {"code": 500, "msg": "缺少必要的依赖库: openpyxl未安装。请使用pip install openpyxl安装openpyxl库以支持Excel文件。"}
                
                try:
                    df = pd.read_excel(file_path)
                except Exception as e:
                    return {"code": 500, "msg": f"读取Excel文件失败: {str(e)}"}
            elif file_type.lower() == 'csv':
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    return {"code": 500, "msg": f"读取CSV文件失败: {str(e)}"}
            else:
                return {"code": 400, "msg": "不支持的文件类型"}
            
            # 根据映射配置重命名列
            # mapping_config格式: {'文件列名': '数据库字段名'}
            df.rename(columns=mapping_config, inplace=True)
            
            # 获取数据库表中存在的字段
            columns_info = self.db.get_table_columns_and_comments(table_name)
            if columns_info is None:
                return {"code": 500, "msg": "获取表字段信息失败"}
            
            db_columns = [col['COLUMN_NAME'] for col in columns_info]
            
            # 过滤掉不在数据库表中的字段
            filtered_columns = [col for col in df.columns if col in db_columns]
            df_filtered = df[filtered_columns]
            
            # 处理NaN值，将其替换为None
            df_filtered = df_filtered.where(pd.notnull(df_filtered), None)
            
            # 将DataFrame转换为插入语句并执行
            inserted_count = 0
            for _, row in df_filtered.iterrows():
                # 构造INSERT语句
                columns_str = ', '.join([f"`{col}`" for col in filtered_columns])
                values_str = ', '.join(['%s' for _ in filtered_columns])
                insert_query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str})"
                
                # 处理空值
                values = []
                for col in filtered_columns:
                    val = row[col]
                    # 转换numpy类型
                    val = self._convert_numpy_types(val)
                    values.append(val)
                
                # 执行插入
                result = self.db.execute_update(insert_query, tuple(values))
                if result:
                    inserted_count += 1
            
            return {
                "code": 200, 
                "msg": "导入成功", 
                "data": {
                    "total_rows": len(df),
                    "inserted_rows": inserted_count
                }
            }
        except Exception as e:
            return {"code": 500, "msg": f"数据导入失败: {str(e)}"}

    def upload_file(self, file):
        """
        上传文件
        
        Args:
            file: Flask请求中的文件对象
            
        Returns:
            dict: 上传结果
        """
        try:
            # 检查文件是否存在
            if not file or not file.filename:
                return {"code": 400, "msg": "未选择文件"}
            
            # 安全地获取文件名
            filename = secure_filename(file.filename)
            if not filename:
                return {"code": 400, "msg": "文件名不合法"}
            
            # 生成唯一文件名
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            
            # 创建日期目录
            date_dir = time.strftime("%Y%m%d")
            save_dir = os.path.join(self.upload_dir, date_dir)
            os.makedirs(save_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(save_dir, unique_filename)
            file.save(file_path)
            
            # 构建文件访问key
            file_key = f"/static/uploads/import/{date_dir}/{unique_filename}"
            
            # 判断文件类型
            file_type = 'unknown'
            if ext.lower() in ['.xls', '.xlsx']:
                file_type = 'excel'
            elif ext.lower() == '.csv':
                file_type = 'csv'
            
            return {
                "code": 200,
                "msg": "上传成功",
                "data": {
                    "file_path": file_path,
                    "file_key": file_key,
                    "file_name": filename,
                    "file_type": file_type
                }
            }
        except Exception as e:
            return {"code": 500, "msg": f"文件上传失败: {str(e)}"}
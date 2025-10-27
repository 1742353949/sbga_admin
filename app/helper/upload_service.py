import os,stat,time
import uuid
from werkzeug.utils import secure_filename
from os import path
from settings import *

class UploadService:
    '''文件上传服务类
    '''
    @staticmethod
    def UploadByFile(file='',temp_file=''):
        """文件上传服务
        
        Args:
            file: 文件
            temp_file: 临时目录，也可以看成是自己的子目录
        Return: return_description
        """
        
        root_path = os.path.join(Config.UPLOAD_DIR, "")
        if temp_file != '':
            root_path = os.path.join(root_path ,temp_file)

        #root_path = path.abspath('') + "/upload"
        config_upload={
            "png",
            "jpg",
            "jpeg"
        }
        
        resp={"code":200,"msg":"操作成功","data":{}}

        # 安全的获取文件名
        filename=secure_filename(file.filename)
        # 获得后缀名,[0]文件名,
        ext=filename.rsplit('.')
        ext = ext[len(ext) - 1]

        #print(ext)
        #print(ext in config_upload)
        
        # 判断后缀名是否在配置中
        if not ext in config_upload:
            resp["code"]=-1
            resp["msg"]="不允许的扩展类型文件"
            #print(resp)
            return resp

        try:
            # 上传目录创建
            file_dir= time.strftime("%Y%m%d")
            save_dir = os.path.join(root_path, file_dir)

            
            if not os.path.exists(save_dir):
                os.makedirs(save_dir,exist_ok=True,mode=0o755)
                os.chmod(save_dir,stat.S_IRWXU | stat.S_IRGRP |stat.S_IRWXO)

            _tmp_name = file_name=str(uuid.uuid4()).replace("_","")
            file_name= _tmp_name +"."+ext
            #save_path = "{0}/{1}".format(save_dir,file_name)
            save_path = os.path.join(save_dir,file_name)
            file.save(save_path)
        
            # 远程目录，ftp上传本地文件至服务器，在本地使用
            #remote_dir = '/static/upload/%s/%s' % (file_dir,file_name)
            #ftp = Ftp()
            #ftp.upload_file(remote_dir,save_path)
            
        except Exception as e:
            resp["code"] = -1
            resp["msg"] = e + "服务器异常,保存图片失败!"
            return resp


        _f_key = "/static/upload/" + file_dir+"/"+file_name
        if temp_file != "":
            _f_key = "/static/upload/" + temp_file + "/" + file_dir + "/" + file_name

        resp["data"]={
            "file_key": _f_key,
            "fname": _tmp_name,
            "path": Config.STATIC_DIR +"/upload/" + temp_file + "/" + file_dir + "/" + file_name
        }
        return resp
    
    @staticmethod
    def UploadByVideo(file='',temp_file=''):
        """文件上传服务
        
        Args:
            file: 文件
            temp_file: 临时目录，也可以看成是自己的子目录
        Return: return_description
        """
        
        root_path = os.path.join(Config.VIDEO_DIR, "upload")
        if temp_file != '':
            root_path = os.path.join(root_path ,temp_file)

        #root_path = path.abspath('') + "/upload"
        config_upload={
            "png",
            "jpg",
            "jpeg",
            "gif",
            "bmp",
            "pdf"
        }
        

        resp={"code":200,"msg":"操作成功","data":{}}

        # 安全的获取文件名
        filename=secure_filename(file.filename)
        # 获得后缀名,[0]文件名,
        ext=filename.rsplit('.')
        ext = ext[len(ext) - 1]

        #print(ext)
        #print(ext in config_upload)
        
        # 判断后缀名是否在配置中
        # if not ext in config_upload:
        #     resp["code"]=-1
        #     resp["msg"]="不允许的扩展类型文件"
        #     #print(resp)
        #     return resp

        if ext in Config.NO_EXISTS_FILE_EXT:
            resp["code"]=-1
            resp["msg"]="不允许的扩展类型文件"
            return resp

        try:
            # 上传目录创建
            file_dir= time.strftime("%Y%m%d")
            save_dir = os.path.join(root_path, file_dir)

            
            if not os.path.exists(save_dir):
                os.makedirs(save_dir,exist_ok=True,mode=0o755)
                os.chmod(save_dir,stat.S_IRWXU | stat.S_IRGRP |stat.S_IRWXO)

            _tmp_name = file_name=str(uuid.uuid4()).replace("_","")
            file_name= _tmp_name +"."+ext
            #save_path = "{0}/{1}".format(save_dir,file_name)
            save_path = os.path.join(save_dir,file_name)
            file.save(save_path)
        
        except Exception as e:
            with open('./upload_video_exception.txt', 'w') as f:
                # 使用str()将异常转换为字符串
                f.write(str(e))
                # 可能还需要记录堆栈跟踪，使用traceback模块
                import traceback
                f.write("\n" + traceback.format_exc())
            
            resp["code"] = -1
            resp["msg"] = e + "服务器异常,保存图片失败!"
            return resp


        _f_key = "/video/upload/" + file_dir+"/"+file_name
        if temp_file != "":
            _f_key = "/video/upload/" + temp_file + "/" + file_dir + "/" + file_name

        resp["data"]={
            "file_key": _f_key,
            "fname": _tmp_name
        }
        return resp
    
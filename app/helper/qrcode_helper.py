import qrcode
from PIL import Image

def generate_qr_code(url, file_name="qrcode.png"):
    """
    生成带网址定向的二维码
    Args:
        url (str): 目标网址
        file_name (str): 生成的二维码图片文件名
    """
    # 创建QRCode对象
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1是最小的
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 控制二维码的错误纠正功能
        box_size=10,  # 控制每个“盒子”的大小
        border=4,  # 控制边框的宽度
    )
    
    # 添加数据
    qr.add_data(url)
    qr.make(fit=True)
    
    # 创建图像
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图像
    img.save(file_name)
    print(f"二维码已生成并保存为 {file_name}")

if __name__ == "__main__":
    import os
    import stat
    # 当前路径
    root_path = os.path.abspath('')
    # 静态文件夹的路径
    STATIC_DIR = os.path.join(root_path, 'static','upload','qrcode')
    if not os.path.exists(STATIC_DIR):
        os.mkdir(STATIC_DIR)
        os.chmod(STATIC_DIR,stat.S_IRWXU | stat.S_IRGRP |stat.S_IRWXO)
    
    url = "https://www.example.com"
    generate_qr_code(url, STATIC_DIR + "/example_qrcode.png")
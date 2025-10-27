# -*- encoding: utf-8 -*-
'''
@file     :   captcha.py
@date     :   2025/03/08 15:30:26
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   图形验证码
'''

from flask import session, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import string
from settings import Config

class Captcha:
    # 生成随机字符串
    def __generate_random_string(self,length=4):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # 生成图形验证码
    def __generate_captcha_image(self,text, width=120, height=40):
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 使用字体（需要在系统中安装字体文件），要用绝对路径
        _ft = Config.STATIC_DIR + "/fonts/arial.ttf"
        font = ImageFont.truetype(_ft, 26)
        
        # 绘制随机字符
        for i, char in enumerate(text):
            x = 10 + i * (width / len(text))
            y = random.randint(5, 10)
            draw.text((x, y), char, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), font=font)
        
        # 添加干扰线
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
        
        return image

    def get_captcha(self,w=120,h=40):
        if w <= 0:
            w = 120
        if h <= 0:
            h = 40
        text = self.__generate_random_string()
        image = self.__generate_captcha_image(text,width=w,height=h)
        
        # 将图像保存到内存中
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 将验证码文本存储在session中
        session['captcha_text'] = text
        
        return send_file(img_io, mimetype='image/png')
    
    def verify_captcha(self,captcha_txt):
        
        return captcha_txt.upper() == session.get('captcha_text')

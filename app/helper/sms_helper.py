# -*- encoding: utf-8 -*-
'''
@file     :   sms_helper.py
@date     :   2025/03/10 06:58:45
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   短信发送帮助类
'''

import requests

class SMSHelper:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://api.unione.com/sms/send"

    def send_sms(self, phone_number, message):
        """ 发送短信
            Args:
                phone_number: 接收短信的手机号码
                message: 短信内容
            Return: 
                发送结果
            @date:   2025/03/10 06:58:45
            @author: snz
        """
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "appId": self.app_id,
            "appSecret": self.app_secret,
            "phoneNumber": phone_number,
            "message": message
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        return response.json()
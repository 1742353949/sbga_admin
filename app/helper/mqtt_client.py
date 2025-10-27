# -*- encoding: utf-8 -*-
'''
@file     :   mqtt_client.py
@date     :   2025/03/09 11:36:35
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   mqtt客户端
'''

import paho.mqtt.client as mqtt
import time,uuid,os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from settings import MQTTConfig

class MQTTClient:
    def __init__(self, client_id="", debug=False):
        self.broker = MQTTConfig.MQTT_BROKER_URL
        self.port = MQTTConfig.MQTT_BROKER_PORT
        self.client_id = client_id if client_id else mqtt._base62(uuid.uuid4().int)[:23]  # 生成一个唯一的 client_id
        self.username = MQTTConfig.MQTT_USERNAME
        self.password = MQTTConfig.MQTT_PASSWORD
        self.client = mqtt.Client(client_id=client_id)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.debug = debug
        # 配置日志记录
        self.configure_logging()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def configure_logging(self):
        if self.debug:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        else:
            # 关闭日志
            logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Connected with result code {rc}")
            self.client.subscribe("test/topic")
        else:
            logging.error(f"Connection failed with result code {rc}")

    def on_message(self, client, userdata, msg):
        logging.info(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

    def on_disconnect(self, client, userdata, rc, properties=None):
        logging.info(f"Disconnected with result code {rc}")

    def connect(self):
        logging.info(f"Connecting to broker {self.broker} on port {self.port}")
        self.client.connect(self.broker, self.port, MQTTConfig.MQTT_KEEPALIVE)
        self.client.loop_start()

    def disconnect(self):
        logging.info("Disconnecting from broker")
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self, topic, qos=0):
        logging.info(f"Subscribing to topic {topic} with QoS {qos}")
        self.client.subscribe(topic, qos)

    def publish(self, topic, payload=None, qos=0, retain=False):
        logging.info(f"Publishing to topic {topic} with payload '{payload}' and QoS {qos}")
        self.client.publish(topic, payload, qos, retain)

    def set_message_callback(self, callback):
        self.client.on_message = callback

# Example usage:
def custom_on_message(client, userdata, msg):
    logging.info(f"Custom message received [{msg.topic}]: {msg.payload.decode()}")
    #print((f"Custom message received [{msg.topic}]: {msg.payload.decode()}"))


if __name__ == "__main__":
    #(broker="broker.hivemq.com") 公开的mqtt服务器
    mqtt_client = MQTTClient(debug=True) 
    mqtt_client.set_message_callback(custom_on_message)
    mqtt_client.connect()
    mqtt_client.subscribe("test/topic")
    mqtt_client.subscribe("demo")
    time.sleep(2)  # Wait for subscription to be successful

    mqtt_client.publish("test/topic", f"Hello MQTT")
    mqtt_client.publish("demo", f"hello demo")
    # Keep the connection open for a while to receive messages
    logging.info("Waiting for messages...")
    time.sleep(10)
    # Disconnect
    mqtt_client.disconnect()
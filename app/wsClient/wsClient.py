import websocket
import threading
import json

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.thread = None
        self.lock = threading.Lock()

    def on_message(self, ws, message):
        print(f"Received from server: {message}")

    def on_error(self, ws, error):
        print(f"Error: {error}")
        self.connect()

    def on_close(self, ws):
        print("### closed ###")
        self.connect()

    def on_open(self, ws):
        print("Connection opened")

    def connect(self):
        def run(*args):
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            self.ws.run_forever()

        self.thread = threading.Thread(target=run)
        self.thread.daemon = True
        self.thread.start()

    def send_message(self, message):
        with self.lock:
            if self.ws :
                self.ws.send(message)
                print(f"send to server:{message}")
            else:
                print("WebSocket is not connected.reconnect...")
                self.connect()
                self.send_message(message)


    def stop(self):
        with self.lock:
            if self.ws:
                self.ws.close()
                self.ws = None
            if self.thread:
                self.thread.join()
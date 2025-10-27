import websocket
import threading
import time

class WebSocketClient:
    def __init__(self, url, reconnect_interval=5, max_reconnect_attempts=None):
        self.url = url
        self.ws = None
        self.thread = None
        self.stop_event = threading.Event()
        self.reconnect_interval = reconnect_interval  # 重连间隔时间（秒）
        self.max_reconnect_attempts = max_reconnect_attempts  # 最大重连次数，None 表示无限重连
        self.reconnect_attempts = 0  # 当前重连次数
        self.running = False  # 用于标记 WebSocketApp 是否正在运行（注意：这不是直接由 WebSocketApp 提供的）

    def on_message(self, ws, message):
        print(f"Received message: {message}")
        # 处理接收到的消息

    def on_error(self, ws, error):
        print(f"Error occurred: {error}")
        # 处理错误，可能包括重连逻辑（但在这里我们让 run_forever 外的循环处理）

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Connection closed with status code {close_status_code} and message: {close_msg}")
        # 连接关闭时，设置 stop_event 以允许 run_forever 外的循环尝试重连
        self.stop_event.set()
        self.running = False  # 更新运行状态

    def on_open(self, ws):
        print("Connection opened")
        # 发送初始消息等

    def run_forever(self):
        while True:
            if self.stop_event.is_set():
                # 如果 stop_event 被设置，则退出循环（但注意，这不会立即停止正在运行的 WebSocketApp）
                break

            try:
                # 创建 WebSocketApp 实例并运行它
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )

                # 使用守护线程来运行 WebSocketApp
                self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
                self.thread.start()

                # 更新运行状态
                self.running = True

                # 等待 WebSocketApp 停止（通过 stop_event 来控制）
                # 注意：这里实际上是在等待 stop_event 被设置，而不是等待 WebSocketApp 真正停止
                while self.running and not self.stop_event.is_set():
                    # 这个循环主要是为了让 run_forever 外的逻辑能够检查 stop_event
                    # 但由于 run_forever 是阻塞的，这个循环体实际上不会执行（除非有异常或 stop_event 被设置）
                    time.sleep(0.1)  # 防止忙等待

                # 如果 WebSocketApp 停止了（由于 stop_event 被设置），则检查是否应该重连
                if not self.stop_event.is_set():  # 实际上这里不会执行，因为 stop_event 已经设置了
                    # 这行代码是为了保持代码结构清晰而保留的，但实际上不会执行到
                    pass

            except Exception as e:
                print(f"WebSocketApp failed to start: {e}")
                # 如果 WebSocketApp 创建或启动失败，则尝试重连
                self.reconnect()

            # 无论是否成功运行，都需要检查 stop_event 和可能的重连逻辑
            if self.stop_event.is_set():
                # 如果 stop_event 被设置，则退出循环（可能是用户请求停止，或者达到了最大重连次数）
                break

            # 如果 WebSocketApp 运行结束了（无论是正常关闭还是由于异常），都尝试重连
            self.reconnect()

    def reconnect(self):
        if self.max_reconnect_attempts is not None and self.reconnect_attempts >= self.max_reconnect_attempts:
            print("Reached maximum reconnect attempts. Stopping.")
            self.stop_event.set()  # 确保 stop_event 被设置，以退出 run_forever 循环
            return

        self.reconnect_attempts += 1
        print(f"Attempting to reconnect... ({self.reconnect_attempts}/{self.max_reconnect_attempts if self.max_reconnect_attempts else '∞'})")
        time.sleep(self.reconnect_interval)

        # 重置 stop_event，以允许尝试下一次连接
        self.stop_event.clear()

    def stop(self):
        self.stop_event.set()
        # 尝试关闭 WebSocket 连接（如果它仍然打开）
        # 注意：由于 run_forever 是阻塞的，并且在新线程中运行，这里关闭连接可能不会立即生效
        # 但是，设置 stop_event 会导致 run_forever 循环在下一次检查时退出
        if self.ws and hasattr(self.ws, 'close'):
            try:
                self.ws.close()
            except Exception as e:
                print(f"Failed to close WebSocket connection: {e}")

# 使用示例
if __name__ == "__main__":
    ws_client = WebSocketClient("ws://124.71.144.85:5001")
    ws_client.run_forever()
    # 要停止客户端，你需要从另一个线程或信号处理器中调用 ws_client.stop()
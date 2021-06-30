import threading
import PID_module


class Session(threading.Thread):
    def __init__(self, client, index, sm):
        threading.Thread.__init__(self)     # 线程初始化
        self.index = index                  # 水箱对象在列表中的下标
        self.height = '0'                   # 当前液位
        self.target = '100'                 # 目标液位
        self.control = '0'                  # 控制量
        self.kp = '0.0'
        self.ki = '0.0'
        self.kd = '0.0'
        # self.history_height = []          # 历史高度
        self.client = client                # socket传输实体对象
        self.exitFlag = True                # 是否退出当前线程，True表示否
        self.isStart = False                # 是否开始发送数据，True表示否
        self.sm = sm                        # 创建该对象的socket_module对象

    def run(self):
        while self.exitFlag:
            try:
                self.height = self.client.recv(512).decode('utf-8')     # 接收客户端发送的数据
            except ConnectionAbortedError or ConnectionResetError:
                print('接收数据失败')
                self.sm.remove(self.index)                              # 在sm列表中移除当前线程
            if self.height is not None and len(self.height) > 0:
                if float(self.height) < 0:                              # 液位小于0作为断开连接信号
                    self.exitPress()                                    # 关闭当前线程
                elif self.isStart:
                    self.pidOutput(float(self.height))                  # pid计算

    # pid计算
    def pidOutput(self, height):
        # if len(self.history_height) <= 100:
        # self.history_height.append(height)                            # 添加历史液位高度
        pid = PID_module.PID(float(self.kp), float(self.ki), float(self.kd), float(self.target))
        pid.update(height)                                              # pid计算
        self.control = str(pid.output)                                  # 结果调节开度
        # 发送数据：Q是调节开度，highaim是目标液位
        senddata = "{'Q':'%f','highaim':'%f'}" % (float(self.control), float(self.target))
        self.client.sendall(bytes(senddata, 'utf8'))

    # 退出当前线程
    def exitPress(self):
        # 目标液位负数作为断开连接信号
        senddata = "{'Q':'%f','highaim':'%f'}" % (float(self.control), -1.0)
        try:
            self.client.sendall(bytes(senddata, 'utf8'))
        except ConnectionAbortedError or ConnectionResetError:
            print('关闭水箱失败')
        self.sm.remove(self.index)      # 在sm列表中移除当前线程
        self.exitFlag = False
        self.isStart = False

    # 开始发送数据
    def startPress(self):
        senddata = "{'Q':'%f','highaim':'%f'}" % (float(self.control), float(self.target))
        self.client.sendall(bytes(senddata, 'utf8'))
        self.isStart = True

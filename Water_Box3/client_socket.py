import socket
import threading


# socket模块
class ClientSocket(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)                                     # 线程初始化
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # 创建socket
        self.addr = ('127.0.0.1', 8888)                                     # socket地址
        self.control = ''                                                   # 控制量
        self.height = 0.0                                                   # 液位
        self.target = ''                                                    # 目标液位
        self.open = 0.0                                                     # 水阀开度
        self.isExit = True                                                  # 是否退出线程，True表示否

    def run(self):
        while self.isExit:
            try:
                data = eval(str(self.socket.recv(1024), 'utf8'))      # 接受控制器发送的信息，highaim对应目标液位，Q对应水阀开度
                # 目标液位为负作为断开连接信号，断开连接
                if float(data['highaim']) < 0:
                    self.target = '-1'
                    self.closeSocket()
                    self.threadExit()
                elif data is not None and len(data) > 0:
                    self.target = data['highaim']           # 获取目标液位
                    self.open = float(data['Q'])            # 获取水阀开度
            except OSError:
                print('获取服务端信息失败')

    # 开始连接
    def connect(self, ip, port):
        self.addr = (ip, int(port))             # 更新地址
        try:
            self.socket.connect(self.addr)      # 根据地址建立socket连接
        except ConnectionRefusedError:
            print('socket连接失败')

    # 发送数据
    def send(self, msg):
        try:
            self.socket.send(msg.encode('utf-8'))
        except OSError:
            print('发送数据失败')

    # 退出当前线程
    def threadExit(self):
        self.isExit = False

    # 关闭socket
    def closeSocket(self):
        try:
            self.socket.shutdown(2)
            self.socket.close()
        except OSError:
            print('关闭socket失败')

    # 通知服务端断开连接，目标液位为负作为断开连接信号
    def bye2Server(self):
        self.send('-1')

import threading
from socket import *
import session


# socket模块
class Socket(threading.Thread):
    def __init__(self, ui, port):
        threading.Thread.__init__(self)                 # 线程初始化
        self.socket = socket(AF_INET, SOCK_STREAM)      # 创建服务端socket
        self.address = ('127.0.0.1', port)              # 连接地址
        self.conn_pool = []                             # 连接池
        self.control = "0.0"                            # 控制量
        self.isSend = False                             # 是否发送数据，True表示发送
        self.ui = ui                                    # 界面对象
        self.me = None                                  # socket_module对象
        self.isExit = True                              # 是否结束线程，True表示否

    def run(self):
        try:
            self.socket.bind(self.address)              # socket绑定地址
            self.socket.listen(3)                       # socket监听三个客户端
            # 循环监听socket连接
            while self.isExit:
                try:
                    # 接受TCP连接并返回（client,addr）,client是套接字对象，用来接收和发送数据；addr是客户端地址
                    client, addr = self.socket.accept()
                    if client is not None:
                        t = session.Session(client, len(self.conn_pool), self.me)       # 创建新线程处理客户端消息
                        self.ui.addClientList(addr, t)                                  # 界面添加客户端
                        self.conn_pool.append(t)                                        # 连接池添加客户端
                        t.start()                                                       # 线程开启
                except OSError:
                    print('接收数据失败')
        except OSError:
            print('服务端已开启')

    # 移除客户端
    def remove(self, index):
        if index < len(self.conn_pool):
            del self.conn_pool[index]           # 连接池移除客户端
            self.ui.delectClientList(index)     # 界面移除客户端

    # 停止当前线程
    def stopThread(self):
        self.isExit = False
        self.socket.close()

import tkinter
from tkinter import *
import socket_module


# 界面视图
class MyUI:
    def __init__(self):
        self.client_list = []       # 客户端地址列表
        self.session_list = []      # 客户端实体列表
        self.index = 0              # 当前客户端下标
        self.time = 20.0            # 当前时间
        self.last_height = 180.0    # 上一次液位
        self.new_height = 180.0     # 当前液位
        self.ui = None              # 本界面对象
        self.s_socket = None        # 服务端socket
        self.isAdd = False          # 液位曲线是否递增，用于获取超调量和波动周期
        self.isStart = False        # 是否开始调控对象

        self.root = Tk()            # tkinter画图工具
        self.root.title('液位控制器')
        self.root.geometry('550x400')
        # 字符串
        self.port = StringVar(value='8888')     # 端口号
        self.client1 = StringVar(value='')      # 水箱对象1
        self.client2 = StringVar(value='')      # 水箱对象2
        self.client3 = StringVar(value='')      # 水箱对象3
        self.client = StringVar(value='')       # 当前选中水箱
        self.kp = StringVar(value='')           # kp
        self.ki = StringVar(value='')           # ki
        self.kd = StringVar(value='')           # kd
        self.height = StringVar(value='')       # 设定的液位
        # 标签
        self.clientAddr_label = Label(self.root, text='客户端地址')
        self.port_label = Label(self.root, text='端口号')
        self.client_label = Label(self.root, text='当前客户端')
        self.height_label = Label(self.root, text='设定液位')
        self.kp_lable = Label(self.root, text="kp")
        self.ki_lable = Label(self.root, text="ki")
        self.kd_lable = Label(self.root, text="kd")
        # 客户端地址列表
        self.clientAddr1_entry = Entry(self.root, textvariable=self.client1, state='disabled')
        self.clientAddr2_entry = Entry(self.root, textvariable=self.client2, state='disabled')
        self.clientAddr3_entry = Entry(self.root, textvariable=self.client3, state='disabled')

        self.port_entry = Entry(self.root, textvariable=self.port)                          # 端口号
        self.client_entry = Entry(self.root, textvariable=self.client, state='disabled')    # 当前客户端
        self.height_entry = Entry(self.root, textvariable=self.height)                      # 设定的液位
        self.kp_entry = Entry(self.root, textvariable=self.kp)
        self.ki_entry = Entry(self.root, textvariable=self.ki)
        self.kd_entry = Entry(self.root, textvariable=self.kd)
        # 按钮
        self.start_btn = Button(self.root, text='开始调节', command=lambda: self.starting())
        self.end_btn = Button(self.root, text='断开连接', command=lambda: self.stopping())
        self.client1_btn = Button(self.root, text='水箱1', command=lambda: self.getClient(0))
        self.client2_btn = Button(self.root, text='水箱2', command=lambda: self.getClient(1))
        self.client3_btn = Button(self.root, text='水箱3', command=lambda: self.getClient(2))
        self.startcontroller_btn = Button(self.root, text='开启控制器', command=lambda: self.startcontroller())
        self.clearCanvas_btn = Button(self.root, text='清空画布', command=lambda : self.clearCanvas())
        # 画布-曲线
        self.canvas1 = Canvas(self.root, bg='white', height=200, width=400)     # 画布对象
        # 排列视图
        self.display()
        # 每隔0.2秒刷新视图
        self.root.after(200, self.update)

    # 排列视图控件
    def display(self):
        self.clientAddr_label.grid(row=1, column=1)
        self.client1_btn.grid(row=3, column=1)
        self.clientAddr1_entry.grid(row=2, column=1)
        self.client2_btn.grid(row=5, column=1)
        self.clientAddr2_entry.grid(row=4, column=1)
        self.client3_btn.grid(row=7, column=1)
        self.clientAddr3_entry.grid(row=6, column=1)
        self.port_label.grid(row=1, column=4)
        self.port_entry.grid(row=1, column=5)
        self.client_label.grid(row=3, column=4)
        self.client_entry.grid(row=3, column=5)
        self.height_label.grid(row=6, column=6, columnspan=3)
        self.height_entry.grid(row=5, column=6, columnspan=6)
        self.startcontroller_btn.grid(row=1, column=6, columnspan=3)
        self.start_btn.grid(row=3, column=6, columnspan=2)
        self.end_btn.grid(row=3, column=8, columnspan=2)
        self.kp_lable.grid(row=5, column=4)
        self.ki_lable.grid(row=6, column=4)
        self.kd_lable.grid(row=7, column=4)
        self.kp_entry.grid(row=5, column=5)
        self.ki_entry.grid(row=6, column=5)
        self.kd_entry.grid(row=7, column=5)
        self.clearCanvas_btn.grid(row=7, column=6, columnspan=3)
        self.canvas1.grid(row=8, column=4, columnspan=5)
        self.drawXY()

    # 画xy轴
    def drawXY(self):
        self.canvas1.create_line(20, 180, 380, 180)        # x轴
        self.canvas1.create_line(20, 180, 20, 20)          # y轴
        # 画y轴坐标
        for i in range(11):
            self.canvas1.create_line(20, 180 - 16 * i, 25, 180 - 16 * i)
            self.canvas1.create_text(10, 180 - 16 * i, text=str(i * 10), activefill="black")
        self.canvas1.create_text(25, 10, text="h", activefill="black")         # 画y轴单位
        # 画x轴坐标
        for i in range(9):
            self.canvas1.create_line(20 + 40 * (i + 1), 180, 20 + 40 * (i + 1), 175)
            self.canvas1.create_text(20 + 40 * (i + 1), 190, text=str((i + 1) * 10 * 2), activefill="black")
        self.canvas1.create_text(390, 175, text="t/s", activefill="black")     # 画x轴单位

    # 显示界面
    def start(self):
        self.root.mainloop()

    # 获取用户点击的客户端下标
    def getClient(self, index):
        self.index = index
        self.updateAll()        # 更新水箱界面

    # 更新水箱界面
    def updateAll(self):
        if len(self.session_list) > self.index:
            client = self.session_list[self.index]      # 获得水箱列表对应下标的水箱对象
            # 更新界面参数
            self.kp.set(client.kp)
            self.ki.set(client.ki)
            self.kd.set(client.kd)
            self.height.set(client.target)
            addr = self.client_list[self.index]         # 获得水箱对象的地址
            self.client.set(str(addr[1]))
            # self.drawHistory()

    # 开启控制器
    def startcontroller(self):
        self.startcontroller_btn['text'] = '已开启'        # 更改启动按钮文字
        self.s_socket = socket_module.Socket(self.ui, int(self.port_entry.get()))   # 启动socket服务端
        self.s_socket.me = self.s_socket                # 传入当前创建的socket对象
        self.s_socket.start()                           # 开始监听客户端连接

    # 清空画布
    def clearCanvas(self):
        self.canvas1.delete(tkinter.ALL)
        self.drawXY()
        self.time = 20.0

    '''
    # 画历史高度曲线
    def drawHistory(self):
        client = self.session_list[self.index]
        list = client.history_height
        x0 = 10.0       # 当前时间
        y0 = 200.0      # 上一次液位
        for i in range(len(list)):
            self.canvas1.create_line(x0, y0, x0 + 0.2, list[i])
            y0 = list[i]
            x0 += 0.2
    '''

    # 启动控制对象(开启水阀)
    def starting(self):
        self.updateClinet()         # 更新水箱参数
        if self.index < len(self.session_list):
            client = self.session_list[self.index]          # 获得水箱列表对应下标的水箱对象
            client.startPress()                             # 开始发送控制数据
            print('开始时间:' + str(self.time / 2 - 10))
            self.isStart = True

    # 停止控制对象（关闭水阀）
    def stopping(self):
        if self.index < len(self.session_list):
            client = self.session_list[self.index]          # 获得水箱列表对应下标的水箱对象
            client.exitPress()                              # 退出关闭对应水箱socket线程
            self.isStart = False

    # 添加客户端列表
    def addClientList(self, addr, session):
        self.client_list.append(addr)
        self.session_list.append(session)
        self.updateList()         # 更新水箱对象列表

    # 删除客户端列表
    def delectClientList(self, index):
        del self.client_list[index]
        del self.session_list[index]
        self.updateList()         # 更新水箱对象列表

    # 更新水箱对象列表
    def updateList(self):
        # 清空水箱列表界面
        self.client1.set('')
        self.client2.set('')
        self.client3.set('')
        # 遍历水箱对象列表更新界面
        for i in range(len(self.client_list)):
            addr = self.client_list[i]      # 获得当前水箱对象地址
            s = addr[0] + ' ' + str(addr[1])
            if i == 0:
                self.client1.set(s)
            elif i == 1:
                self.client2.set(s)
            else:
                self.client3.set(s)

    # 更新水箱参数
    def updateClinet(self):
        if self.index < len(self.session_list):
            client = self.session_list[self.index]          # 获得水箱列表对应下标的水箱对象
            # 将用户输入的值设入水箱对象中
            client.kp = self.kp_entry.get()
            client.ki = self.ki_entry.get()
            client.kd = self.kd_entry.get()
            client.target = self.height_entry.get()

    # 更新液位曲线
    def update(self):
        if self.time < 380:                             # 坐标范围限定
            self.canvas1.create_line(self.time, self.last_height, self.time + 0.4, self.new_height)     # 两点画线
            self.time += 0.4                            # 更新x坐标
            # 更新新、旧液位高度
            if len(self.session_list) > self.index:
                self.last_height = self.new_height
                client = self.session_list[self.index]          # 获得水箱列表对应下标的水箱对象
                if client.height is not None and len(client.height) > 0:
                    self.new_height = 180 - float(client.height) * 1.6
                else:
                    self.new_height = 180
            else:
                self.last_height = 180
                self.new_height = 180
            # 打印峰值时间与超调量
            if self.isStart and self.isAdd and self.new_height > self.last_height:
                print('达到峰值的时间：' + str(self.time / 2 - 10))
                if len(self.session_list) > 0:
                    client = self.session_list[self.index]
                    print('超调量:' + client.height)
            self.isAdd = True if self.new_height < self.last_height else False
            self.root.after(200, self.update)

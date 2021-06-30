import random
from tkinter import *
import socket
import time
from tkinter import Canvas
from tkinter import scrolledtext

import client_socket


# ui界面
class ClientUI:
    def __init__(self):
        self.in_max = 1000                  # 最大入水阀水量
        self.out_max = 1000                 # 最大出水阀水量
        self.box_high = 100                 # 水箱高度
        self.box_area = 10000               # 水箱底面积
        self.time = 0.2                     # 采样时间
        self.high_now = 0.0                 # 当前液位
        self.high_last = 0.0                # 上一次液位
        self.high_delta = 0.0               # 目标液位
        self.percent = 0.0                  # 开度
        self.last_percent = 0.0             # 上一次开度
        self.socket = None                  # 客户端socket
        self.isStart = False                # 是否开始连接，True表示是
        self.out = False                    # 画布是否创建出水图片，True表示是
        self.in1 = False                    # 画布是否创建入水图片，True表示是
        self.in2 = False                    # 画布是否创建入水图片，True表示是

        self.root = Tk()                    # tkinter画图工具
        self.root.title('水箱模型')
        self.root.geometry('600x400')

        self.waterin = self.initImgIn()     # 入水图片集合
        self.waterout = self.initImgOut()   # 出水图片集合
        self.sk = socket.socket()           # 创建socket对象
        self.server_ip = '127.0.0.1'        # 默认ip
        # StringVar，tkinter编辑框文字
        self.height_now = StringVar(value='0.0')        # 当前液位
        self.height_target = StringVar(value='')        # 目标液位
        self.ip = StringVar(value=self.server_ip)       # ip
        # 标签
        self.ip_label = Label(self.root, text='控制器IP')
        self.port_label = Label(self.root, text='端口号')
        self.c_label = Label(self.root, text='当前液位')
        self.s_label = Label(self.root, text='目标液位')
        self.recorde_label = Label(self.root, text='聊天记录')
        # 文本框
        self.ip_entry = Entry(self.root, textvariable=self.ip)                                  # ip输入
        self.port_entry = Entry(self.root, textvariable=StringVar(value='8888'), show=None)     # 端口输入
        self.c_entry = Entry(self.root, textvariable=self.height_now, state='disabled')         # 当前液位
        self.s_entry = Entry(self.root, textvariable=self.height_target, state='disabled')      # 目标液位
        self.recorde = scrolledtext.ScrolledText(self.root, width=50, height=15)                # 状态栏
        # 按钮
        self.connect_btn = Button(self.root, text='建立连接', command=lambda: self.started())
        # 画布
        self.canvas1 = Canvas(self.root, bg='white', height=200, width=200)
        self.canvas11 = Canvas(self.root, bg='black', height=100, width=100)
        # 绘制水箱
        self.image_box = PhotoImage(file="image\\box.png")
        self.canvas1.create_image(0, 0, anchor='nw', image=self.image_box)
        # 绘制液面
        self.image_water = PhotoImage(file="image\\water.png")
        self.water_canvas = self.canvas11.create_image(0, 0, anchor='nw', image=self.image_water)
        # 布局
        self.display()

        self.root.mainloop()

    # 加载入水动画图片
    def initImgIn(self):
        res = list()
        res.append(PhotoImage(file="image\\water_in2.png"))
        res.append(PhotoImage(file="image\\water_in4.png"))
        res.append(PhotoImage(file="image\\water_in6.png"))
        res.append(PhotoImage(file="image\\water_in8.png"))
        res.append(PhotoImage(file="image\\water_in10.png"))
        return res

    # 加载出水动画图片
    def initImgOut(self):
        res = list()
        res.append(PhotoImage(file="image\\water_out2.png"))
        res.append(PhotoImage(file="image\\water_out4.png"))
        res.append(PhotoImage(file="image\\water_out6.png"))
        res.append(PhotoImage(file="image\\water_out8.png"))
        res.append(PhotoImage(file="image\\water_out10.png"))
        return res

    # 控件布局
    def display(self):
        self.c_label.grid(row=3, column=0)
        self.c_entry.grid(row=3, column=1)
        self.s_label.grid(row=4, column=0)
        self.s_entry.grid(row=4, column=1)
        self.connect_btn.grid(row=2, column=1)
        self.ip_entry.grid(row=0, column=1)
        self.ip_label.grid(row=0, column=0)
        self.port_entry.grid(row=1, column=1)
        self.port_label.grid(row=1, column=0)
        self.recorde_label.grid(row=6, column=1)
        self.recorde.grid(row=8, column=1)
        self.canvas1.grid(row=8, column=0)
        self.canvas11.grid(row=8, column=0)
        self.root.after(200, self.update)

    # 开始连接
    def started(self):
        self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + 'connecting...\n')      # 状态栏打印连接状态
        self.socket = client_socket.ClientSocket()                          # 创建socket
        self.socket.connect(self.ip_entry.get(), self.port_entry.get())     # socket连接
        self.socket.start()                                                 # 开启socket线程
        self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + ' connect success\n')      # 状态栏打印连接状态
        self.isStart = True

    # 液面计算函数
    def delta_t(self):
        # y(k) = 1.96 * y(k-1) - 0.9608 * y(k-2) + 0.000392 * u(k-1) + 0.0003895 * u(k-2)       # 多水箱模型
        # y(k) = 0.003807 * u(k-1) + 0.9848 * y(k-1)                                            # 单水箱模型
        q = self.in_max * self.percent / 100 * self.time                            # 由水阀开度计算出水流量
        self.high_delta = 0.000392 * q + 1.96 * self.high_now - 0.9608 * self.high_last + 0.0003895 * self.last_percent \
                          - self.high_now                                           # 计算液面变化量
        self.last_percent = q                                                       # 更新上一次调节量
        self.high_last = self.high_now                                              # 更新上一次液位

    # 更新数据
    def update(self):
        if self.isStart:
            self.percent = self.socket.open     # 获取控制器发送的调节量
            # 目标液位为负作为断开连接信号，断开连接
            print(self.socket.target)
            if len(self.socket.target) > 0 and float(self.socket.target) < 0:
                self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + ' 连接已断开' + '\n')       # 状态栏打印连接状态
                print('test')
                # 删除水流动画
                if self.out:
                    self.canvas1.delete('out')
                elif self.in1 or self.in2:
                    self.canvas1.delete('in1')
                    self.canvas11.delete('in2')
            else:
                self.height_target.set(self.socket.target)      # 设置目标液面
                self.delta_t()                                  # 液面计算
                self.moveit()                                   # 水箱液位更新
                interfere = 0 if self.high_now == 0 else random.uniform(-0.05, 0.05)      # 生成干扰量
                print('干扰液位:' + str(interfere))
                fake_high = self.high_now + interfere
                self.socket.send(str(fake_high))                # 发送当前液位给控制器
                # 状态栏打印水阀开度
                if self.percent > 0:
                    self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + ' 入水阀开度:' + str(self.percent) + '\n')
                elif self.percent < 0:
                    self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + ' 出水阀开度:' + str(-self.percent) + '\n')
                else:
                    self.recorde.insert(INSERT, time.strftime('%Y-%m-%d %H:%M:%S') + ' 水阀关闭' + '\n')
        self.root.after(200, self.update)

    # 更新水流图片
    def changeSize(self, water):
        index = int(abs(self.high_delta) / 0.6)     # 计算水流大小，获取图集下标
        index = index if index < 5 else 4
        index = index if index >= 0 else 0
        return water[index]

    # 更新液位&画图
    def moveit(self):
        if 0 <= self.high_now + self.high_delta <= 100:                     # 当液位处于0到100的区间内
            self.high_now += self.high_delta                                # 更新液位值
            self.canvas11.move(self.water_canvas, 0, -self.high_delta)      # 更新模型液位高度
            self.height_now.set(self.high_now)                              # 更新液面
        elif self.high_now + self.high_delta < 0:                           # 当液位小于0时
            self.canvas11.move(self.water_canvas, 0, self.high_now)
            self.high_now = 0
            self.height_now.set(0)
        elif self.high_now + self.high_delta > 100:                         # 当液位大于100时
            self.canvas11.move(self.water_canvas, 0, self.high_now - 100)
            self.high_now = 100
            self.height_now.set(100)
        # 绘制水流动画
        if self.high_delta > 0:                     # 液位上升
            if self.out:
                self.canvas1.delete('out')          # 移除出水图片
            img = self.changeSize(self.waterin)     # 根据增量获取对应入水图片
            # 设置入水图片
            self.in1 = self.canvas1.create_image(92, 30, anchor='nw', image=img, tags='in1')
            self.in2 = self.canvas11.create_image(42, 0, anchor='nw', image=img, tags='in2')
        elif self.high_delta < 0:                   # 液位下降
            # 移除入水图片
            if self.in1 or self.in2:
                self.canvas1.delete('in1')
                self.canvas11.delete('in2')
            img = self.changeSize(self.waterout)     # 根据增量获取对应出水图片
            self.out = self.canvas1.create_image(92, 180, anchor='nw', image=img, tags='out')       # 设置出水图片
        else:                                       # 液位不变，移除图片
            if self.out:
                self.canvas1.delete('out')
            elif self.in1 or self.in2:
                self.canvas1.delete('in1')
                self.canvas11.delete('in2')

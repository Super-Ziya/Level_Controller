from ui_module import ClientUI

# 模拟对象主函数
if __name__ == '__main__':
    app = ClientUI()                    # 初始化界面
    if app.socket is not None and app.socket.socket is not None:
        app.socket.threadExit()         # 退出socket线程
        app.socket.bye2Server()         # 通知控制器
        app.socket.closeSocket()        # 关闭socket
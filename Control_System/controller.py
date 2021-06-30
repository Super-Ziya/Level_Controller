import ui_module

# 控制器主函数
if __name__ == '__main__':
    ui = ui_module.MyUI()           # 初始化界面
    ui.ui = ui                      # 创建的界面对象赋给ui
    ui.start()                      # 显示界面
    if ui.s_socket is not None:
        # 遍历连接池，释放连接
        for session in ui.s_socket.conn_pool:
            session.exitPress()
        ui.s_socket.stopThread()    # 停止socket服务端

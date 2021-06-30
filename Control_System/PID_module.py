# pid模块
class PID:
    def __init__(self, p=0.0, i=0.0, d=0.0, target=30.0):
        self.kp = p
        self.ki = i
        self.kd = d
        self.target = target                # 目标液位值
        self.error_1 = 0.0                  # e(k-1)
        self.error_2 = 0.0                  # e(k-2)
        self.error_3 = 0.0                  # e(k-3)
        self.error_4 = 0.0                  # e(k-4)
        self.output = 0.0                   # 输出
        self.last_output = 0.0              # 上一次的输出
        self.s = 10000                      # 底面积
        self.Rs = 1.8                       # 水阻
        self.dt = 0.2                       # 采样时间
        self.current = 1000                 # 入水阀流量

    # 滤波：e(k) - e(k-1) = e(k) + 3e(k-1) - 3e(k-2) - e(k-3)
    def update(self, feedback):
        error = self.target - feedback      # e(k)
        self.output = self.incrementalPID(error)
        self.height2open(feedback)          # 调节量转水阀开度

    # 位置式：△u = Kp*e(k) + KI Ee(i) + KD[e(k)-e(k-1)]
    def positionPID(self, error):
        pTerm = self.kp * error
        iTerm = self.ki * self.error_2
        dTerm = self.kd * (error - self.error_1)
        self.error_2 += error
        self.error_1 = error
        return pTerm + iTerm + dTerm

    # 增量式：△u = Kp[e(k)-e(k-1)] + Ki*e(k) + Kd[e(k)-2e(k-1)+e(k-2)]
    # 四点中值差分：e(k)-e(k-1) = △e(k) = 1/6[e(k)+3e(k-1)-3e(k-2)-e(k-3)]
    def incrementalPID(self, error):
        # 加滤波
        delta_e = (error + 3 * self.error_1 - 3 * self.error_2 - self.error_3) / 6
        delta_e_1 = (self.error_1 + 3 * self.error_2 - 3 * self.error_3 - self.error_4) / 6
        pTerm = self.kp * delta_e                                       # 比例环节
        iTerm = self.ki * error                                         # 积分环节
        dTerm = self.kd * (delta_e - delta_e_1) + self.last_output      # 微分环节 + 上次输出

        # 无滤波
        # pTerm = self.kp * (error - self.error_1)                                            # 比例环节
        # iTerm = self.ki * error                                                             # 积分环节
        # dTerm = self.kd * (error - 2 * self.error_1 + self.error_2) + self.last_output      # 微分环节 + 上次输出

        # 更新上一次输出
        self.last_output = self.output
        # 更新误差
        self.error_4 = self.error_3
        self.error_3 = self.error_2
        self.error_2 = self.error_1
        self.error_1 = error
        return pTerm + iTerm + dTerm

    # 液位调节量转水龙头开度
    def height2open(self, feedback):
        v = self.output * self.s            # 调节水量
        # 加水操作
        if v > 0:
            open = v / self.current
            self.output = 100 if 100 < open else open
        # 出水操作
        elif v < 0:
            close = v * self.Rs / feedback
            self.output = -100 if -100 > close else close
        # 不用操作
        else:
            self.output = 0.0

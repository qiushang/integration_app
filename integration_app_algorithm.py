# -*- coding: utf8 -*-
# 打包所有的信号处理自定义函数
import numpy as np
from scipy.signal import detrend, lfilter, buttord, butter
import matplotlib.pyplot as plt
import os
import re


def integration_time_domain(acc, sps, bb, aa):
    acc = detrend(acc)
    acc = lfilter(bb, aa, acc)
    n = len(acc)
    dt = 1 / sps
    vel = [0, ]
    for k in range(1, n):
        vel.append(vel[k - 1] + dt * ((acc[k - 1] + acc[k]) / 2))
    vel = lfilter(bb, aa, vel)
    vel = detrend(vel)
    disp = [0, ]
    for k in range(1, n):
        disp.append(disp[k - 1] + dt * ((vel[k - 1] + vel[k]) / 2))
    disp = detrend(disp)
    return vel, disp, acc


def integration_file(sps, file_to_integrate, stop_freq, pass_freq, filter_type, input_type):
    """
    :param sps: 采样频率
    :param file_to_integrate: 待积分的文件（含路径）
    :param stop_freq: 滤波器参数
    :param pass_freq: 滤波器参数
    :param filter_type: 滤波器参数
    :param input_type: 输入文件类型
    :return:
    """
    if input_type == "kinemetrics":
        fp = open(file_to_integrate, "r")
        data = fp.readlines()
        fp.close()
        data = [float(d[0:-1]) for d in data]
        acc = [data, ]
    elif input_type == "仅加速度序列":
        fp = open(file_to_integrate, "r")
        data = fp.readlines()
        fp.close()
        line1 = data[0][0:-1].split("\t")
        try:
            test = [float(d) for d in line1]
            flag = -1
        except:
            flag = -2
        data = [d[0:flag].split("\t") for d in data]
        data = np.array(data)
        data = data.T
        acc = []
        for i in range(1, len(data)):
            acc.append([float(item) for item in data[i]])

    elif input_type == "eZAnalyst":
        # 读取数据 和 sps
        fp = open(file_to_integrate, "r")
        data0 = fp.readlines()
        data1 = data0[10:]
        sps = 1 / float(data0[3][19:-1])
        print(file_to_integrate, "读取到的sps: ", sps)
        data = [d[0:-2].split("\t") for d in data1]
        data = np.array(data)
        data = data.T
        acc = []
        for i in range(0, len(data)):
            acc.append([float(item) for item in data[i]])

    elif input_type == "时间-加速度序列":
        fp = open(file_to_integrate, "r")
        data = fp.readlines()
        fp.close()
        line1 = data[0][0:-1].split("\t")
        line2 = data[1][0:-1].split("\t")
        try:
            test = [float(d) for d in line1]
            flag = -1
        except:
            flag = -2
        sps = 1/(float(line2[0]) - float(line1[0]))

        data = [d[0:flag].split("\t") for d in data]
        data = np.array(data)
        data = data.T
        acc = []
        for i in range(1, len(data)):
            acc.append([float(item) for item in data[i]])
    else:
        print("非法输入类型参数")
        return 0, 0, 0

    # 计算滤波器参数
    N, Wn = buttord(2*pass_freq/sps, 2*stop_freq/sps, 3, 40, False)
    bb, aa = butter(N, Wn, filter_type, False)

    vel = []
    disp = []
    filter_acc = []
    for i in range(0, len(acc)):
        vel_i, disp_i, filter_acc_i = integration_time_domain(acc[i], sps, bb, aa)
        vel.append(vel_i)
        disp.append(disp_i)
        filter_acc.append(filter_acc_i)

    return vel, disp, filter_acc, acc, sps


def output_file(disp_data, vel_data, file_name, output_type):
    if output_type == "仅速度":
        col_len = len(vel_data)
        row_len = len(vel_data[0])
        vel_out = file_name[0:-4] + "_vel.txt"
        fp_vel = open(vel_out, "w+")
        fp_vel.close()
        fp_vel = open(vel_out, "a+")
        for i in range(0, row_len):
            for j in range(0, col_len):
                fp_vel.write(str(vel_data[j][i]))
                fp_vel.write("\t")
            fp_vel.write("\n")

    elif output_type == "仅位移":
        col_len = len(disp_data)
        row_len = len(disp_data[0])
        disp_out = file_name[0:-4] + "_disp.txt"
        fp_disp = open(disp_out, "w+")
        fp_disp.close()
        fp_disp = open(disp_out, "a+")
        for i in range(0, row_len):
            for j in range(0, col_len):
                fp_disp.write(str(disp_data[j][i]))
                fp_disp.write("\t")
            fp_disp.write("\n")

    elif output_type == "速度和位移":
        col_len = len(disp_data)
        row_len = len(disp_data[0])
        vel_out = file_name[0:-4] + "_disp.txt"
        disp_out = file_name[0:-4] + "_vel.txt"

        fp_vel = open(vel_out, "w+")
        fp_vel.close()
        fp_vel = open(vel_out, "a+")
        for i in range(0, row_len):
            for j in range(0, col_len):
                fp_vel.write(str(vel_data[j][i]))
                fp_vel.write("\t")
            fp_vel.write("\n")

        fp_disp = open(disp_out, "w+")
        fp_disp.close()
        fp_disp = open(disp_out, "a+")
        for i in range(0, row_len):
            for j in range(0, col_len):
                fp_disp.write(str(disp_data[j][i]))
                fp_disp.write("\t")
            fp_disp.write("\n")

    else:
        print("输出类型参数不合法")


if __name__ == "__main__":
    pass


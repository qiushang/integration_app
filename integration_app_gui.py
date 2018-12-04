# -*- coding: utf8 -*-
import sys
import os
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabWidget, QWidget, QApplication, QFormLayout, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QRadioButton, QLabel, QPushButton, QListWidget, QSizePolicy
from PyQt5.QtWidgets import QTextEdit, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import integration_app_algorithm as algo
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from numpy import arange, sin, pi
from PyQt5.QtCore import pyqtSignal


class MyMplCanvas(FigureCanvas):
    """FigureCanvas的最终的父类其实是QWidget。"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        self.axes1 = self.fig.add_subplot(221)  # 建立一个子图，如果要建立复合图，可以在这里修改
        # self.axes1.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        self.axes2 = self.fig.add_subplot(222)  # 建立一个子图，如果要建立复合图，可以在这里修改
        # self.axes2.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        self.axes3 = self.fig.add_subplot(223)  # 建立一个子图，如果要建立复合图，可以在这里修改
        # self.axes3.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        self.axes4 = self.fig.add_subplot(224)  # 建立一个子图，如果要建立复合图，可以在这里修改
        # self.axes4.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # self.fig.tight_layout()


    '''绘制静态图，可以在这里定义自己的绘图逻辑'''

    def acc_plot(self, t, s):
        # t = arange(0.0, 3.0, 0.01)
        # s = sin(2 * pi * t)
        self.axes1.clear()
        self.axes1.set_title('原始加速度')
        self.axes1.plot(t, s)
        # self.axes1.set_ylabel('原始加速度')
        # self.axes1.set_xlabel('时间')
        self.axes1.grid(True)

    def filter_acc_plot(self, t, s):
        # t = arange(0.0, 3.0, 0.01)
        # s = 2*sin(2 * pi * t)
        self.axes2.clear()
        self.axes2.set_title('滤波后加速度')
        self.axes2.plot(t, s)
        # self.axes2.set_ylabel('滤波后加速度')
        # self.axes2.set_xlabel('时间')
        self.axes2.grid(True)

    def vel_plot(self, t, s):
        # t = arange(0.0, 3.0, 0.01)
        # s = 3*sin(2 * pi * t)
        self.axes3.clear()
        self.axes3.set_title('速度')
        self.axes3.plot(t, s)
        # self.axes3.set_ylabel('速度')
        # self.axes3.set_xlabel('时间')
        self.axes3.grid(True)

    def disp_plot(self, t, s):
        # t = arange(0.0, 3.0, 0.01)
        # s = 4*sin(2 * pi * t)
        self.axes4.clear()
        self.axes4.set_title('位移')
        self.axes4.plot(t, s)
        # self.axes4.set_ylabel('位移')
        # self.axes4.set_xlabel('时间')
        self.axes4.grid(True)
        self.fig.tight_layout()


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=50, height=40, dpi=100)

        self.mpl_ntb = NavigationToolbar(self.mpl, self)  # 添加完整的 toolbar

        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)


class IntegrationAPP(QTabWidget):
    new_ack_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(IntegrationAPP, self).__init__(parent)
        self.ack_content = ""
        self.files_to_integrate = []
        self.file_pre_integrate = ""
        self.input_type = 0
        self.output_type = 0
        self.sps = 0
        self.filter_type = "highpass"
        self.stop_freq = 0.2
        self.pass_freq = 0.4

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")

        self.tab1UI()
        self.tab2UI()

        self.new_ack_signal.connect(self.update_ack_box)

        self.setWindowTitle("加速度一键积分程序")

    def tab1UI(self):
        # 帧布局
        self.ui = MatplotlibWidget()
        self.setTabText(0, "参数选择")
        # 在标签1中添加这个帧布局
        # self.tab1.setLayout(layout)
        tab1_layout = QVBoxLayout()
        filter_layout = QHBoxLayout()

        open_file_layout = QHBoxLayout()
        self.open_file_btn = QPushButton("选择预积分文件")
        self.file_line = QLineEdit()
        open_file_layout.addWidget(self.open_file_btn)
        open_file_layout.addSpacing(10)
        open_file_layout.addWidget(self.file_line)
        self.open_file_btn.clicked.connect(self.select_file)

        self.filter_label = QLabel()
        self.filter_label.setText("滤波器参数设置：")
        filter_layout.addWidget(self.filter_label)
        filter_layout.addSpacing(5)
        self.filter_combox = QComboBox()
        self.filter_combox.addItem("highpass")
        self.stop_freq_label = QLabel()
        self.stop_freq_label.setText("Stop Freq：")
        self.stop_freq_line = QLineEdit()
        self.stop_freq_line.setText("0.2")
        filter_layout.addWidget(self.filter_combox)
        filter_layout.addSpacing(15)
        filter_layout.addWidget(self.stop_freq_label)
        filter_layout.addSpacing(5)
        filter_layout.addWidget(self.stop_freq_line)
        filter_layout.addSpacing(15)
        self.pass_freq_label = QLabel()
        self.pass_freq_label.setText("Pass Freq：")
        self.pass_freq_line = QLineEdit()
        self.pass_freq_line.setText("0.4")
        filter_layout.addWidget(self.pass_freq_label)
        filter_layout.addSpacing(5)
        filter_layout.addWidget(self.pass_freq_line)
        filter_layout.addSpacing(15)
        self.show_wave_btn = QPushButton("计算并查看波形")
        self.show_wave_btn.clicked.connect(self.pre_integration)
        filter_layout.addWidget(self.show_wave_btn)
        filter_layout.addSpacing(15)

        self.visual_channel_label = QLabel()
        self.visual_channel_label.setText("显示图形通道：")
        filter_layout.addWidget(self.visual_channel_label)
        filter_layout.addSpacing(5)
        self.visual_channel_combox = QComboBox()
        # self.visual_channel_combox.addItem("0")
        filter_layout.addWidget(self.visual_channel_combox)
        filter_layout.addSpacing(5)



        file_io_layout = QHBoxLayout()

        self.file_type_label = QLabel()
        self.file_type_label.setText("指定输入文件类型：")
        self.file_type_combox = QComboBox()
        self.file_type_combox.addItem("kinemetrics")
        self.file_type_combox.addItem("eZAnalyst")
        self.file_type_combox.addItem("仅加速度序列")
        self.file_type_combox.addItem("时间-加速度序列")

        self.file_output_label = QLabel()
        self.file_output_label.setText("指定输出文件类型：")
        self.file_output_combox = QComboBox()
        self.file_output_combox.addItem("仅速度")
        self.file_output_combox.addItem("仅位移")
        self.file_output_combox.addItem("速度和位移")

        self.sps_label = QLabel()
        self.sps_label.setText("指定样本采样率：")
        self.sps_line = QLineEdit()

        file_io_layout.addWidget(self.file_type_label)
        # file_io_layout.addSpacing(10)
        file_io_layout.addWidget(self.file_type_combox)
        file_io_layout.addSpacing(20)
        file_io_layout.addWidget(self.file_output_label)
        file_io_layout.addWidget(self.file_output_combox)
        file_io_layout.addSpacing(20)
        file_io_layout.addWidget(self.sps_label)
        file_io_layout.addWidget(self.sps_line)

        output_type_layout = QHBoxLayout()
        self.output_type_label = QLabel()
        self.output_type_label.setText("指定输出文件类型：")
        self.output_vel = QRadioButton("输出速度")
        self.output_disp = QRadioButton("输出位移")
        self.output_vel_and_disp = QRadioButton("输出速度和位移")
        output_type_layout.addWidget(self.output_type_label)
        output_type_layout.addWidget(self.output_vel)
        output_type_layout.addWidget(self.output_disp)
        output_type_layout.addWidget(self.output_vel_and_disp)

        tab1_layout.addItem(open_file_layout)
        tab1_layout.addSpacing(10)
        tab1_layout.addItem(file_io_layout)
        tab1_layout.addSpacing(10)
        tab1_layout.addItem(filter_layout)
        tab1_layout.addWidget(self.ui)

        self.tab1.setLayout(tab1_layout)
        tab1_layout.setAlignment(Qt.AlignTop)

    # 同理如上
    def tab2UI(self):
        self.setTabText(1, "一键积分")
        # self.tab2.setLayout(layout)
        tab2_layout = QHBoxLayout()
        tab2_layout_col1 = QVBoxLayout()
        tab2_layout_col2 = QVBoxLayout()
        tab2_layout_col1_sub = QHBoxLayout()
        self.get_file_btn = QPushButton("选择待积分文件")
        self.get_file_btn.clicked.connect(self.list_file_name)
        self.file_list_box = QListWidget()
        self.file_list_box.itemClicked.connect(self.list_item_clicked)
        self.integration = QPushButton("一键积分")
        self.integration.clicked.connect(self.one_key_integration)
        self.clear_file_btn = QPushButton("清除列表")
        self.clear_file_btn.clicked.connect(self.clear_file_list_box)
        tab2_layout_col1_sub.addWidget(self.integration)
        tab2_layout_col1_sub.addSpacing(5)
        tab2_layout_col1_sub.addWidget(self.clear_file_btn)
        tab2_layout_col1.addWidget(self.get_file_btn)
        tab2_layout_col1.addSpacing(5)
        tab2_layout_col1.addWidget(self.file_list_box)
        tab2_layout_col1.addSpacing(5)
        tab2_layout_col1.addItem(tab2_layout_col1_sub)

        self.label_show_ack = QLabel()
        self.label_show_ack.setText("显示区域")
        self.show_ack_box = QTextEdit()
        self.show_ack_box.setReadOnly(True)
        self.clear_ack_btn = QPushButton("清空")
        self.clear_ack_btn.clicked.connect(self.clear_show_ack_box)

        tab2_layout_col2.addWidget(self.label_show_ack)
        tab2_layout_col2.addSpacing(5)
        tab2_layout_col2.addWidget(self.show_ack_box)
        tab2_layout_col2.addSpacing(5)
        tab2_layout_col2.addWidget(self.clear_ack_btn)

        tab2_layout.addItem(tab2_layout_col1)
        tab2_layout.addSpacing(5)
        tab2_layout.addItem(tab2_layout_col2)

        # tab2_layout.setStretch(0, 1)
        # tab2_layout.setStretch(1, 4)
        self.tab2.setLayout(tab2_layout)

    def select_file(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setFilter(QDir.Files)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.file_pre_integrate = filenames[0]
            if "eZAnalyst" in self.file_pre_integrate:
                self.file_type_combox.setCurrentIndex(1)
            elif "KMI" in self.file_pre_integrate:
                self.file_type_combox.setCurrentIndex(0)
            self.file_line.setText(self.file_pre_integrate)
            # self.files_to_integrate = self.files_to_integrate + filenames
            # self.update_file_list_box()

    def get_paras_from_ui(self, choice):
        self.input_type = self.file_type_combox.currentText()
        self.output_type = self.file_output_combox.currentText()
        self.sps = self.sps_line.text()
        self.filter_type = self.filter_combox.currentText()
        self.stop_freq = float(self.stop_freq_line.text())
        self.pass_freq = float(self.pass_freq_line.text())
        # 输入文件类型 kinemetrics  和  仅加速度序列  需要手动指定加速度
        # 输入文件类型 eZAnalyst    和  时间-加速度序列  直接从文件中读取加速度数据
        if not choice:
            if not os.path.isfile(self.file_pre_integrate):
                QMessageBox.warning(self, "提示", "请先指定合法预积分文件！")
                return 1

        if self.input_type == "kinemetrics" or self.input_type == "仅加速度序列":
            if not len(self.sps):
                QMessageBox.warning(self, "提示", "请指定样本采样率")
                return 2
            else:
                self.sps = float(self.sps)

        if self.input_type == "eZAnalyst" or self.input_type == "时间-加速度序列":
            if len(self.sps):
                QMessageBox.about(self, "提示", "自动读取样本采样率，无需指定")

        print("预积分文件：", self.file_pre_integrate)
        print("输入文件类型：", self.input_type)
        print("输出文件类型：", self.output_type)
        print("采样率：", self.sps)
        print("filter：", self.filter_type)
        print("stop freq：", self.stop_freq)
        print("pass freq：", self.pass_freq)
        return 0

    def pre_integration(self):
        if not self.get_paras_from_ui(0):
            # QMessageBox.about(self, "提示", "正在计算，计算完毕该窗口自动关闭")
            self.vel, self.disp, self.filter_acc, self.acc, self.sps = algo.integration_file(self.sps, self.file_pre_integrate, self.stop_freq, self.pass_freq, self.filter_type, self.input_type)

            self.t = arange(0.0, len(self.acc[0])/self.sps, 1/self.sps)

            self.visual_channel_combox.clear()
            for i in range(0, len(self.acc)):
                self.visual_channel_combox.addItem(str(i+1))
            self.visual_channel_combox.currentIndexChanged.connect(self.visual_channel_change)

            # ui = MatplotlibWidget()
            self.visual_channel_change()

    def visual_channel_change(self):
        if len(self.visual_channel_combox.currentText()):
            channel = int(self.visual_channel_combox.currentText()) - 1
            self.ui.mpl.acc_plot(self.t, self.acc[channel])
            self.ui.mpl.filter_acc_plot(self.t, self.filter_acc[channel])
            self.ui.mpl.vel_plot(self.t, self.vel[channel])
            self.ui.mpl.disp_plot(self.t, self.disp[channel])
            self.ui.mpl.draw()

    def list_file_name(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setFilter(QDir.Files)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.files_to_integrate = self.files_to_integrate + filenames
            self.update_file_list_box()

    def update_file_list_box(self):
        self.file_list_box.clear()
        for item in self.files_to_integrate:
            self.file_list_box.addItem(item)
        # self.file_list_box.item(0).setForeground(QColor(Qt.red))

    def one_key_integration(self):
        if not self.get_paras_from_ui(1):
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.DirectoryOnly)
            if dlg.exec_():
                storage_path = dlg.selectedFiles()[0]
                print("数据输出文件夹：", storage_path)
                for item in self.files_to_integrate:
                    try:
                        vel, disp, filter_acc, acc, sps = algo.integration_file(self.sps, item, self.stop_freq, self.pass_freq, self.filter_type, self.input_type)
                        info = item + "  积分完毕"
                        self.ack_content = self.ack_content + "<font color='green'>" + info + "</font><br>"
                        self.new_ack_signal.emit()
                        _, file_name = os.path.split(item)
                        algo.output_file(disp, vel, os.path.join(storage_path, file_name), self.output_type)
                        info = item + "  输出完毕"
                        self.ack_content += "<font color='green'>" + info + "</font><br>"
                        self.new_ack_signal.emit()
                    except:
                        info = item + "异常"
                        self.ack_content += "<font color='red'>" + info + "</font><br>"
                        self.new_ack_signal.emit()

    def clear_file_list_box(self):
        self.file_list_box.clear()

    def list_item_clicked(self, item):
        choice = QMessageBox.warning(self, "更改", "是否移除选中文件？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.files_to_integrate.remove(item.text())
            self.update_file_list_box()

    def clear_show_ack_box(self):
        self.ack_content = ""
        self.update_ack_box()

    def update_ack_box(self):
        self.show_ack_box.setHtml(self.ack_content)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    demo = IntegrationAPP()
    demo.show()
    sys.exit(app.exec_())

    """
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    # ui.mpl.start_static_plot()  # 测试静态图效果
    # ui.mpl.start_dynamic_plot() # 测试动态图效果
    ui.show()
    sys.exit(app.exec_())
    """

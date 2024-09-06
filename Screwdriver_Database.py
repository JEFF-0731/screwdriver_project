import configparser
import copy
import gc
import threading
import time
from datetime import datetime

import numpy as np
import os
import sys

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableWidgetItem, QHeaderView, QHBoxLayout, QLineEdit
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from Screwdriver_Database_Window import Ui_Screwdriver_Database_Window
from Postgres_API import SQL_aoi_allresults_detail
from Postgres_API import SQL_aoi_ng_detail
import tkinter as tk
from tkinter import messagebox
import socket

class DB_MainWindow(QtWidgets.QMainWindow, Ui_Screwdriver_Database_Window):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        self.setupUi(self)

        self.tableWidget_aoi_allresults_detail.setVisible(False)
        self.tableWidget_aoi_ng_detail.setVisible(False)
        self.pushButton_ReadData.setVisible(False)
        self.pushButton_StartTest.setVisible(False)

        self.iniGuiEvent()
        self.database_informatoin = {}
        self.read_ini()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        for child in self.groupBox_database_information.findChildren(QLineEdit):
            accessible_name = child.accessibleName()
            if accessible_name in self.database_informatoin:
                child.setText(self.database_informatoin[accessible_name])
        self.database_isOpen = False
        print(self.database_informatoin['ip'])
        try:
            self.AOI_detail_SQL = SQL_aoi_allresults_detail(IP=self.database_informatoin['ip'],
                                                            port=self.database_informatoin['port'],
                                                            user=self.database_informatoin['username'],
                                                            password=self.database_informatoin['password'],
                                                            database=self.database_informatoin['database'])
            self.AOI_NG_detail_SQL = SQL_aoi_ng_detail(IP=self.database_informatoin['ip'],
                                                       port=self.database_informatoin['port'],
                                                       user=self.database_informatoin['username'],
                                                       password=self.database_informatoin['password'],
                                                       database=self.database_informatoin['database'])
            self.label_connect_status.setText('連線成功')
            self.database_isOpen = True
        except:
            self.label_connect_status.setText('連線失敗')
        # threading.Thread(target=self.write_data_Test, args=()).start()
        # DATA = self.AOI_detail_SQL.get_barcode('M11-2303001')
        # for i, a in enumerate(['awm_key', 'eqp_management_no', 'wo', 'mpp_sn', 'part_no', 'part_name', 'prod_qty']):
        #     print(f'{a} = {DATA[i]}')


        # self.tableWidget_aoi_allresults_detail.setColumnCount(7)
        # self.tableWidget_aoi_allresults_detail.setRowCount(2)
        # self.tableWidget_aoi_allresults_detail.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_aoi_allresults_detail.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.tableWidget_aoi_ng_detail.setColumnCount(5)
        # self.tableWidget_aoi_ng_detail.setRowCount(2)
        # self.tableWidget_aoi_ng_detail.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_aoi_ng_detail.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)

        # self.awm_key = "M11-2303001-0051"
        # self.sn =
        # self.aoi_start =datetime.now()
        # self.aoi_end =datetime.now()
        # self.aoi_cv_lead_time =
        # self.aoi_op_lead_time =
        # self.pass_or_failure =
        # self.ng_bits_index = ''

        # data_information = {
        #     "awm_key": 'self.awm_key',
        #     "sn": 'self.sn',
        #     "aoi_start": f'{self.aoi_start .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
        #     "aoi_end": f'{self.aoi_end.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
        #     "aoi_cv_lead_time": str((self.aoi_end - self.aoi_start).total_seconds()),
        #     "aoi_op_lead_time": 0,
        #     "pass_or_failure": False,
        # }
        # try:
        #     self.AOI_detail_SQL.post_table_one_data(table_name="aoi_allresults_detail", data=data_information)
        # except Exception as e:
        #     print(f'資料庫 : aoi_allresults_detail --> Error\n{e}')
        #
        # data_ng = {
        #     "awm_key": 'self.awm_key',
        #     "sn": 'self.sn',
        #     "ng1": '5',
        #     "ng2": "",
        #     "ng3": ""
        # }
        # try:
        #     self.AOI_NG_detail_SQL.post_table_one_data(table_name="aoi_ng_detail", data=data_ng)
        # except Exception as e:
        #     print(LineBot().send_line('資料庫 : aoi_ng_detail --> Error'))
        #     print(f'資料庫 : aoi_ng_detail --> Error\n{e}')

    def get_aoi_recipe_master_datas(self, part_no):
        # Fetch the data using the given barcode
        DATA = self.AOI_detail_SQL.get_barcode_aoi_recipe_master(part_no)

        # Define the keys for the dictionary
        keys = ['part_no', 'aoi_tpe_code', 'img_data1', 'img_data2', 'img_data3', 'para1', 'para2', 'para3']

        # Create a dictionary by zipping the keys with the data
        data_dict = {keys[i]: DATA[i] for i in range(len(keys))}

        # Return the dictionary
        return data_dict
    def get_aoi_op_master_datas(self, awm_key):
        # Fetch the data using the given barcode
        DATA = self.AOI_detail_SQL.get_barcode(awm_key)

        # Define the keys for the dictionary
        try:
            keys = ['awm_key', 'eqp_management_no', 'wo', 'mpp_sn', 'part_no', 'part_name', 'prod_qty']
        except:
            keys = ['awm_key', 'eqp_management_no', 'wo', 'part_no', 'part_name', 'prod_qty', 'wo_status', 'wo_creation_date']

        # Create a dictionary by zipping the keys with the data
        data_dict = {keys[i]: DATA[i] for i in range(len(keys))}

        # Return the dictionary
        return data_dict
        # DATA = self.AOI_detail_SQL.get_barcode('M11-2303001')
        # for i, a in enumerate(['awm_key', 'eqp_management_no', 'wo', 'mpp_sn', 'part_no', 'part_name', 'prod_qty']):
        #     print(f'{a} = {DATA[i]}')

    def iniGuiEvent(self):
        self.pushButton_ReadData.clicked.connect(self.read_data)
        self.pushButton_StartTest.clicked.connect(self.Read_SN)
        self.pushButton_connectiontest.clicked.connect(self.connectiontest)
    def change(self):
        config = configparser.ConfigParser()
        config.read('Screwdriver_Database.ini')
        for key in self.database_informatoin.keys():
            config['information'][key] = self.database_informatoin[key]
        with open('Screwdriver_Database.ini', 'w') as conf:
            config.write(conf)

    def showerror(self, hintMessage):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title='error', message=hintMessage)

    def clear_all_line_edits(self):
        for line_Edit in self.groupBox_database_information.children():
            if hasattr(line_Edit, 'setText'):
                line_Edit.setText('')
    def connectiontest(self):
        # for child in self.groupBox_database_information.findChildren(QLineEdit):
        #     accessible_name = child.accessibleName()
        #     if accessible_name in self.database_informatoin:
        #         child.setText(self.database_informatoin[accessible_name])
        print(self.lineEdit_password.text())
        self.AOI_detail_SQL = None
        self.AOI_NG_detail_SQL = None
        gc.collect()
        try:
            self.AOI_detail_SQL = SQL_aoi_allresults_detail(IP=self.lineEdit_ip.text(),
                                                            port=self.lineEdit_port.text(),
                                                            user=self.lineEdit_username.text(),
                                                            password=self.lineEdit_password.text(),
                                                            database=self.lineEdit_database.text())
            self.AOI_NG_detail_SQL = SQL_aoi_ng_detail(IP=self.lineEdit_ip.text(),
                                                       port=self.lineEdit_port.text(),
                                                       user=self.lineEdit_username.text(),
                                                       password=self.lineEdit_password.text(),
                                                       database=self.lineEdit_database.text())
            self.label_connect_status.setText('連線成功')
            print('連線成功')
            self.change()

            self.label_connect_status.setStyleSheet("background-color: white;")
            self.lineEdit_ip.setStyleSheet("background-color: white;")
            self.lineEdit_port.setStyleSheet("background-color: white;")
            self.lineEdit_username.setStyleSheet("background-color: white;")
            self.lineEdit_password.setStyleSheet("background-color: white;")
            self.lineEdit_database.setStyleSheet("background-color: white;")
        except:
            self.label_connect_status.setText('連線失敗')
            self.label_connect_status.setStyleSheet("background-color: red;")
            self.lineEdit_ip.setStyleSheet("background-color: red;")
            self.lineEdit_port.setStyleSheet("background-color: red;")
            self.lineEdit_username.setStyleSheet("background-color: red;")
            self.lineEdit_password.setStyleSheet("background-color: red;")
            self.lineEdit_database.setStyleSheet("background-color: red;")

        # finally:
        #     self.clear_all_line_edits()


    def read_ini(self):
            config = configparser.ConfigParser()
            config.read('Screwdriver_Database.ini')
            for key in config['information']:
                self.database_informatoin[key] = config['information'][key]


    def write_data(self):
        if self.database_isOpen:
            data_information = {
                "awm_key": self.awm_key,
                "sn": self.sn,
                "aoi_start": f'{self.aoi_start.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
                "aoi_end": f'{self.aoi_end.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
                "aoi_cv_lead_time": str((self.aoi_end - self.aoi_start).total_seconds()),
                "aoi_op_lead_time": self.aoi_op_lead_time,
                "pass_or_failure": self.pass_or_failure,
                "isfirstchk": self.isfirstchk
            }
            try:
                self.AOI_detail_SQL.post_table_one_data(table_name="aoi_allresults_detail", data=data_information)
                self.isfirstchk = True
            except Exception as e:
                print(f'資料庫 : aoi_allresults_detail --> Error\n{e}')
                self.showerror('資料庫錯誤\n請重新開啟程式')

            data_ng = {
                "awm_key": self.awm_key,
                "sn": self.sn,
                "ng1": self.ng_bits_index,
                "ng2": "",
                "ng3": "",
                '"manulChk"': self.manulChk
            }
            try:
                self.AOI_NG_detail_SQL.post_table_one_data(table_name="aoi_ng_detail", data=data_ng)
            except Exception as e:
                # print(LineBot().send_line('資料庫 : aoi_ng_detail --> Error'))
                print(f'資料庫 : aoi_ng_detail --> Error\n{e}')
                self.showerror('資料庫錯誤\n請重新開啟程式')


            if self.pass_or_failure:
                print('All Pass')
                try:
                    self.AOI_NG_detail_SQL.delete_table_one_data("aoi_ng_detail", self.awm_key, self.sn)
                except Exception as e:
                    # print(LineBot().send_line('資料庫 : aoi_ng_detail --> Error'))
                    print(f'資料庫 : delete_table_one_data --> Error\n{e}')
        else:
            print('database is not connected')

    def write_data_Test(self):
        for i in range(0, 50):
            data_ng = {
                "awm_key": 'self.awm_key',
                "sn": f'self.sn_{i}',
                "ng1": 'self.ng_bits_index',
                "ng2": "",
                "ng3": ""
            }
            try:
                self.AOI_NG_detail_SQL.post_table_one_data(table_name="aoi_ng_detail", data=data_ng)
            except Exception as e:
                # print(LineBot().send_line('資料庫 : aoi_ng_detail --> Error'))
                print(f'資料庫 : aoi_ng_detail --> Error\n{e}')

            if i%10 == 0:
                print('delete_table_one_data')
                self.AOI_NG_detail_SQL.delete_table_one_data("aoi_ng_detail", 'self.awm_key', f'self.sn_{i}')
        # count = 0
        # while True:
        #     count += 1
        #     self.aoi_start = datetime.now()
        #     self.aoi_end = datetime.now()
        #     self.aoi_op_lead_time = 0
        #     self.pass_or_failure = False
        #     data_information = {
        #         "awm_key": 'self.awm_key',
        #         "sn": 'self.sn',
        #         "aoi_start": f'{self.aoi_start.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
        #         "aoi_end": f'{self.aoi_end.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}',
        #         "aoi_cv_lead_time": str((self.aoi_end - self.aoi_start).total_seconds()),
        #         "aoi_op_lead_time": self.aoi_op_lead_time,
        #         "pass_or_failure": self.pass_or_failure,
        #     }
        #     try:
        #         self.AOI_detail_SQL.post_table_one_data(table_name="aoi_allresults_detail", data=data_information)
        #     except Exception as e:
        #         print(f'資料庫 : aoi_allresults_detail --> Error\n{e}')
        #
        #     data_ng = {
        #         "awm_key": 'self.awm_key',
        #         "sn": 'self.sn',
        #         "ng1": '1,2,3',
        #         "ng2": "",
        #         "ng3": ""
        #     }
        #     try:
        #         if count % 500 == 0:
        #             self.AOI_NG_detail_SQL.post_table_one_data(table_name="aoi_ng_detail", data=data_ng)
        #     except Exception as e:
        #         print(LineBot().send_line('資料庫 : aoi_ng_detail --> Error'))
        #         print(f'資料庫 : aoi_ng_detail --> Error\n{e}')
        #     time.sleep(0.1)

    def read_data(self):
        # 調用所有資料
        all_data = self.AOI_detail_SQL.get_table_all_data(table_name="aoi_allresults_detail")
        print(all_data)
        # 设置列数和行数
        if not (len(all_data) == 0):
            self.tableWidget_aoi_allresults_detail.setColumnCount(len(all_data[0]))
            self.tableWidget_aoi_allresults_detail.setRowCount(len(all_data))

            # 设置表头
            all_data[0].keys()
            header = [str(k) for k in all_data[0].keys()]
            # print(header)
            # header = ['aoi_end', 'aoi_op_lead_time', 'pass_or_failure', 'aoi_start', 'aoi_cv_lead_time', 'sn', 'awm_key']
            self.tableWidget_aoi_allresults_detail.setHorizontalHeaderLabels(header)

            # 填充数据
            for row, item in enumerate(all_data):
                for column, key in enumerate(header):
                    value = item[key]
                    Witem = QTableWidgetItem(str(value))
                    self.tableWidget_aoi_allresults_detail.setItem(row, column, Witem)

            # 设置表格自动调整列宽
            self.tableWidget_aoi_allresults_detail.resizeColumnsToContents()
            # print(all_data)

        all_data = self.AOI_NG_detail_SQL.get_table_all_data(table_name="aoi_ng_detail")
        if not (len(all_data) == 0):
            # 調用所有資料
            # 设置列数和行数
            self.tableWidget_aoi_ng_detail.setColumnCount(len(all_data[0]))
            self.tableWidget_aoi_ng_detail.setRowCount(len(all_data))

            # 设置表头
            header = [str(k) for k in all_data[0].keys()]
            self.tableWidget_aoi_ng_detail.setHorizontalHeaderLabels(header)

            # 填充数据
            for row, item in enumerate(all_data):
                for column, key in enumerate(header):
                    value = item[key]
                    Witem = QTableWidgetItem(str(value))
                    self.tableWidget_aoi_ng_detail.setItem(row, column, Witem)

            # 设置表格自动调整列宽
            self.tableWidget_aoi_ng_detail.resizeColumnsToContents()
            # print(all_data)
    def creat_Serial_Number(self):
        self.sn = f'SN_{"%03d" % self.Read_SN()}'
    def reset_data(self, awm_Key='Test'):
        # self.awm_key = awm_Key
        self.sn = ''
        self.aoi_start = ''
        self.aoi_end = ''
        self.aoi_cv_lead_time = 0
        self.aoi_op_lead_time = 0
        self.pass_or_failure = False
        self.ng_bits_index = ''
        self.isfirstchk = True
        self.manulChk = False

    def Read_SN(self):
        print('Read_SN_in')
        print(f'self.database_isOpen:{self.database_isOpen}')
        if self.database_isOpen:
            try:
                # 調用單筆資料
                KEY = {
                    "awm_key": self.awm_key,
                }
                one_data = self.AOI_detail_SQL.get_table_one_data_onlyawm_key(table_name="aoi_allresults_detail", key=KEY)
                print(f'總共有 {"%05d" % len(one_data)} 筆')
                print(one_data)
                return len(one_data) + 1
            except Exception as e:
                print(f'資料庫 : Read_SN --> Error\n{e}')
                return 0
        else:
            return 0

    def showerror(self, hintMessage):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title='error', message=hintMessage)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = DB_MainWindow()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
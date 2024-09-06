import copy
import sys
import threading
from datetime import datetime, timedelta
import time
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableWidgetItem, QHeaderView, QLabel
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
import yaml
from PLC.IOcardQthread import IOcard

from Screwdriver_LogIn_Window import Ui_Screwdriver_LogIn_Form
from Screwdriver_Detection_Window import Ui_Screwdriver_Detection_Window

from Camera import Camera
from ScrewDrive import ScrewDrive
from Modbus import Modbus
from Screwdriver_Database import DB_MainWindow
from Motor import Motor
from Lock import Lock
import logging
import configparser
import tkinter as tk
from tkinter import messagebox
import datetime
import os


class Screwdriver_EngineerMode_LogIn(QtWidgets.QMainWindow, Ui_Screwdriver_LogIn_Form,Ui_Screwdriver_Detection_Window):
    def __init__(self, myini=None):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        self.setupUi(self)
        self.initGuiEvent()

        self.Myini = myini

    def initGuiEvent(self):
        pass
        # self.pushButton_login.clicked.connect(self.logIn)

    def logIn(self):
        try:
            if self.lineEdit_password.text() == self.Myini.engineer_mode_login_password and self.lineEdit_username.text() != '':
                self.writeToTXT(self.lineEdit_username.text(), 'pass')
                self.lineEdit_username.setText('')
                self.lineEdit_password.setText('')
                return True
            elif self.lineEdit_username.text() == '' or self.lineEdit_password.text() == '':
                self.showerror('帳號或密碼不能為空')
                self.writeToTXT(self.lineEdit_username.text(), 'fail')
                self.lineEdit_username.setText('')
                self.lineEdit_password.setText('')
                return False
            else:
                self.showerror('密碼錯誤')
                self.writeToTXT(self.lineEdit_username.text(), 'fail')
                self.lineEdit_username.setText('')
                self.lineEdit_password.setText('')
                return False
        except Exception as e:
            self.showerror('錯誤')
            print(e)
            return False

    def showerror(self, hintMessage): #改成class
        root = tk.Tk() #解決 多跳一個messengeBox 關不掉
        root.withdraw() #多跳一個messengeBox 關不掉
        messagebox.showerror(title='error', message=hintMessage)

    def writeToTXT(self, username, islogin):
        if not os.path.exists(r".\EngineerMode_LogIn_Record"):
            os.makedirs(r".\EngineerMode_LogIn_Record")
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
        log_filename = now.strftime('%Y-%m-%d') + ".txt"
        log_entry = f"{now.strftime('%Y/%m/%d_%H-%M-%S')}, {islogin}, {username}\n"
        with open(os.path.join(r".\EngineerMode_LogIn_Record", log_filename), 'a') as log_file:
            log_file.write(log_entry)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = Screwdriver_EngineerMode_LogIn()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
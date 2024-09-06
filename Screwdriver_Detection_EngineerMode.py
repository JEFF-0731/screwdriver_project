import copy
import os
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

from Screwdriver_Detection_EngineerMode_Window import Ui_Screwdriver_Detection_EngineerMode_Window
from Screwdriver_Detection_Window import Ui_Screwdriver_Detection_Window

from Camera import Camera
from ScrewDrive import ScrewDrive
from Modbus import Modbus
from Screwdriver_Database import DB_MainWindow
from Motor import Motor
from Lock import Lock
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


class Screwdriver_Detection_EngineerMode(QtWidgets.QMainWindow, Ui_Screwdriver_Detection_EngineerMode_Window,Ui_Screwdriver_Detection_Window):
    Recipe_Change_Signal = pyqtSignal()
    def __init__(self, myplc=None, myini=None, public_camera=None):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        self.setupUi(self)
        self.initGuiEvent()
        self.label_Image.setScaledContents(True)

        self.Myini = myini
        self.comboBox_recipe.addItems([recipe for recipe in self.Myini.recipes])
        self.comboBox_recipe.setCurrentText('請選擇產品')

        self.load_translations()

        self.dbwindow = DB_MainWindow()

        if myplc==None:
            self.IOCardThread = IOcard(SERVER_HOST='192.168.0.150', SERVER_PORT=502)
            self.IOCardConnect()
        else:
            self.IOCardThread = myplc
        self.camera = public_camera
        self.camera.FreeRun.connect(self.EngineerMode_FreeRun)

        self.label_plc_m20.setStyleSheet("background-color: Red")
        self.label_plc_m21.setStyleSheet("background-color: Red")
        self.label_plc_m22.setStyleSheet("background-color: Red")
        self.label_plc_m23.setStyleSheet("background-color: Red")
        self.label_plc_m24.setStyleSheet("background-color: Red")
        self.label_plc_m25.setStyleSheet("background-color: Red")
        self.label_plc_m26.setStyleSheet("background-color: Red")
        self.label_plc_m27.setStyleSheet("background-color: Red")
        self.label_plc_m28.setStyleSheet("background-color: Red")
        self.label_plc_m29.setStyleSheet("background-color: Red")
        self.label_plc_m0.setStyleSheet("background-color: Red")
        self.label_plc_m1.setStyleSheet("background-color: Red")
        self.label_plc_m2.setStyleSheet("background-color: Red")
        self.label_plc_m3.setStyleSheet("background-color: Red")
        self.label_plc_m6.setStyleSheet("background-color: Red")


    def initGuiEvent(self):
        self.checkBox_language_zh.clicked.connect(lambda: self.language_change('zh'))
        self.checkBox_language_en.clicked.connect(lambda: self.language_change('en'))
        self.checkBox_language_pt.clicked.connect(lambda: self.language_change('pt'))
        self.checkBox_language_tv.clicked.connect(lambda: self.language_change('tv'))

        self.checkBox_AI_Light_On.stateChanged.connect(self.checkBox_AI_Light_checkStateChange)
        # self.checkBox_AI_Light_Off.stateChanged.connect(self.checkBox_AI_Light_checkStateChange)
        self.checkBox_AOI_Light_On.stateChanged.connect(self.checkBox_AOI_Light_checkStateChange)
        # self.checkBox_AOI_Light_Off.stateChanged.connect(self.checkBox_AOI_Light_checkStateChange)

        self.pushButton_Motor_Out.clicked.connect(self.on_btn_motor_out_clicked)
        self.pushButton_Motor_In.clicked.connect(self.on_btn_motor_in_clicked)

        self.comboBox_recipe.currentIndexChanged.connect(self.Recipe_Change)

        self.pushButton_Change_TakeImage_File_Route.clicked.connect(self.change_takeImage_file_route)
        self.pushButton_Open_TakeImage_File_Route.clicked.connect(self.open_takeImage_file_route)
        self.pushButton_open_dbWindow.clicked.connect(self.open_dbWindow)

    def open_dbWindow(self):
        self.dbwindow.show()

    def showerror(self, hintMessage):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title='error', message=hintMessage)

    def open_takeImage_file_route(self):
        try:
            if os.path.exists(f'{self.takeImage_file_route}') == False:
                self.showerror('請先設定路徑')
            elif os.path.exists(f'{self.takeImage_file_route}') == True:
                os.startfile(self.takeImage_file_route)
            else:
                self.showerror('錯誤')
        except:
            self.showerror('請先設定路徑')

    def change_takeImage_file_route(self):
        root = tk.Tk()
        root.withdraw()
        try:
            self.takeImage_file_route = filedialog.askdirectory()
            self.label_TakeImage_File_Route.setText(self.takeImage_file_route)
            print(self.takeImage_file_route)
            if os.path.exists(f'{self.takeImage_file_route}/AI') == False:
                os.makedirs(f'{self.takeImage_file_route}/AI')
            if os.path.exists(f'{self.takeImage_file_route}/AOI') == False:
                os.makedirs(f'{self.takeImage_file_route}/AOI')
        except:
            self.takeImage_file_route = ''
            self.showerror('路徑錯誤')

    def EngineerMode_FreeRun(self):
        Result = cv2.flip(self.camera.Image_RealTime, 1)
        Result = cv2.resize(Result, (340, 186), interpolation=cv2.INTER_AREA)
        self.imageLable_Show(self.label_Image, cv2.rotate(Result, cv2.ROTATE_90_CLOCKWISE))
    def Recipe_Change(self):
        self.Recipe_Change_Signal.emit()
        print(f'{self.comboBox_recipe.currentText()}')
    def load_translations(self):
        file_path = './i18n_language/translations.yaml'
        with open(file_path, 'r', encoding='utf-8') as file:
            self.translations = yaml.safe_load(file)

    def language_change(self, lang):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Ui_Screwdriver_Detection_EngineerMode_Window",
                                      f'<html><head/><body><p align="center"><span style="font-weight:600; font-size:55pt;">{self.translations.get(lang, {}).get("mode", "")}</span></p></body></html>'))

    def IOCardConnect(self):
        self.IOCardThread.IOCard_connect()
        if self.IOCardThread.connect:
            self.debugBar('IOCard Connection!!!')
            self.IOCardThread.open()
            self.IOCardThread.start()
            self.IOCardThread.rawdataINPUT.connect(self.showPLCState)
            self.IOCardThread.rawdataMOTOR.connect(self.showPLCStateMotor)
        else:
            self.debugBar('IOCard Disconnection!!!')

    def showPLCState(self, input0,input1,input2,input3,input4,input5,input6,input7,input8,input9):
        if input0:
            self.label_plc_m20.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m20.setStyleSheet("background-color: Red")
        if input1:
            self.label_plc_m21.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m21.setStyleSheet("background-color: Red")
        if input2:
            self.label_plc_m22.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m22.setStyleSheet("background-color: Red")
        if input3:
            self.label_plc_m23setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m23.setStyleSheet("background-color: Red")
        if input4:
            self.label_plc_m24.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m24.setStyleSheet("background-color: Red")
        if input5:
            self.label_plc_m25.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m25.setStyleSheet("background-color: Red")
        if input6:
            self.label_plc_m26.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m26.setStyleSheet("background-color: Red")
        if input7:
            self.label_plc_m27.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m27.setStyleSheet("background-color: Red")
        if input8:
            self.label_plc_m28.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m28.setStyleSheet("background-color: Red")
        if input9:
            self.label_plc_m29.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m29.setStyleSheet("background-color: Red")

    def showPLCStateMotor(self, input0,input1,input2,input3,input4):
        if input0:
            self.label_plc_m0.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m0.setStyleSheet("background-color: Red")
        if input1:
            self.label_plc_m1.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m1.setStyleSheet("background-color: Red")
        if input2:
            self.label_plc_m2.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m2.setStyleSheet("background-color: Red")
        if input3:
            self.label_plc_m3setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m3.setStyleSheet("background-color: Red")
        if input4:
            self.label_plc_m6.setStyleSheet("background-color: lightgreen")
        else:
            self.label_plc_m6.setStyleSheet("background-color: Red")

    def checkBox_AI_Light_checkStateChange(self):
        if self.IOCardThread.connect:
            if self.checkBox_AI_Light_On.isChecked() == True:
                self.debugBar('IOCard Connection!!!')
                self.IOCardThread.openAILight()
            elif self.checkBox_AI_Light_On.isChecked() == False:
                self.IOCardThread.closeAll()
        else:
            self.debugBar('IOCard Disconnection!!!')

    def checkBox_AOI_Light_checkStateChange(self):
        if self.IOCardThread.connect:
            if self.checkBox_AOI_Light_On.isChecked() == True:
                self.debugBar('IOCard Connection!!!')
                self.IOCardThread.openAOILight()
            elif self.checkBox_AOI_Light_On.isChecked() == False:
                self.IOCardThread.closeAll()
        else:
            self.debugBar('IOCard Disconnection!!!')

    def on_btn_motor_out_clicked(self):
        if self.IOCardThread.connect:
            self.debugBar('IOCard Connection!!!')
            self.IOCardThread.updataDisSpeed(310, 400)
        else:
            self.debugBar('IOCard Disconnection!!!')

    def on_btn_motor_in_clicked(self):
        if self.IOCardThread.connect:
            self.debugBar('IOCard Connection!!!')
            self.IOCardThread.updataDisSpeed(-310, 400)
        else:
            self.debugBar('IOCard Disconnection!!!')

    def debugBar(self, msg):
        self.statusBar().showMessage(str(msg), 5000)
    def imageLable_Show(self, image_label, Show_image):
        Show_image = cv2.cvtColor(Show_image, cv2.COLOR_BGR2RGB)  # 圖像存儲使用8-8-8 24位RGB格式
        rows, cols, channels = Show_image.shape  # 獲取圖片長寬
        QImg = QImage(Show_image.data, cols, rows, cols*channels, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = Screwdriver_Detection_EngineerMode()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
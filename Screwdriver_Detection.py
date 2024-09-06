from yc_SCANNER.prod.tw.com.yctools.util.hw.barCodeReader import abfactory
from yc_SCANNER.prod.tw.com.yctools.util.hw.barCodeReader import CINO_S680
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

from Screwdriver_Detection_Window import Ui_Screwdriver_Detection_Window
from Camera import Camera
from ScrewDrive import ScrewDrive
from Modbus import Modbus
from Screwdriver_Database import DB_MainWindow
from Motor import Motor
from Lock import Lock
import logging
from Myini import Myini
from Screwdriver_Detection_EngineerMode import Screwdriver_Detection_EngineerMode
from Screwdriver_EngineerMode_LogIn import Screwdriver_EngineerMode_LogIn

import gc
import yaml
from PLC.IOcardQthread import IOcard
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import configparser



class Screwdriver_Detection(QtWidgets.QMainWindow, Ui_Screwdriver_Detection_Window):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        print('Screwdriver_Detection0509')
        self.setupUi(self)
        self.pushButton_Load_Recipe.setStyleSheet(
            'background-color: 	#4CAF50; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  #green
        self.pushButton_Recipe_End.setStyleSheet(
            'background-color: 	#FF5555; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  #red

        self.timer = QTimer(self)

        # set logging file
        self.iniLogging()
        self.dev_logger.info('Program(Screwdriver_Detection) Start')
        lock = Lock(dev_logger=self.dev_logger)
        self.MYINI = Myini()

        self.label_Image.setScaledContents(True)

        # self.motor = Motor()
        # if self.motor.Motor_isOpen:
        #     self.motor.MotorInit()
        #     self.motor_idle_timer = QTimer(self)#設定IO卡閒置重新連線計時器
        #     self.motor_idle_timer.start(60000)#設定馬達閒置重平台移進去時間間隔為60秒
        # # self.serialPort = SerialPort()
        # self.modbus = Modbus(self.dev_logger)
        # if self.modbus.Modbus_isOpen:
        #     self.modbus_reconnect_timer = QTimer(self)  # 設定IO卡閒置重新連線計時器
        #     self.modbus_reconnect_timer.start(60000)  # 設定IO卡閒置重新連線計時器啟用時間間隔為60秒

        # self.Identity = ['alpha', 'beta']

        self.IOCardThread = IOcard(SERVER_HOST='192.168.0.150', SERVER_PORT=502, dev_logger=self.dev_logger)
        self.IOCardConnect()

        if self.IOCardThread.connect:
            self.motor_idle_timer = QTimer(self)  # 設定IO卡閒置重新連線計時器
            self.motor_idle_timer.start(75000)#設定馬達閒置重平台移進去時間間隔為60秒

        self.camera = Camera()
        if self.camera.Camera_isOpen:
            self.camera.start()

        self.dbwindow = DB_MainWindow()

        self.login_window = Screwdriver_EngineerMode_LogIn(self.MYINI)
        self.engineer_mode_window = Screwdriver_Detection_EngineerMode(self.IOCardThread, self.MYINI, self.camera)

        self.iniGuiEvent()

        self.screwdrives = list()
        for i, k in enumerate(self.MYINI.Identity_CodeName):
            sd = ScrewDrive(r".\model", self.dev_logger, k, myIni=self.MYINI)
            sd.report.connect(self.NG_Report)
            sd.status.connect(self.statusChange)
            self.screwdrives.append(sd)

        self.countdown_seconds = 0
        self.is_Timeup = False
        self.NG_Count = 0
        self.Start24_Count = 0
        self.real_detect_amount = 0
        self.passdetect_amount = 0 #合格數量
        self.comboBox_recipe.addItems([recipe for recipe in self.MYINI.recipes])
        self.comboBox_recipe.setVisible(False)
        self.pushButton_TakeImage.setVisible(False)
        self.pushButton_24Hours.setVisible(False)

        # self.exposure_time_tuple = (23000, 25000, 27000, 29000, 31000, 36000)
        # self.exposure_time_tuple = (18000, 20000, 22000, 24000, 26000, 28000)
        # self.exposure_time_tuple = (33000, 35000, 37000, 39000, 41000, 36000)#5張AI 1張AOI
        self.exposure_time_tuple_AI = (33000, 35000, 37000, 39000, 41000)
        self.exposure_time_tuple_AOI = (32000, 34000, 36000, 38000, 40000)

        # self.dbwindow.awm_key = 'M11-2303001'

        self.IOCardThread.openYellowLight_closeDetctLight()

        self.pushButton_TakeImage.setEnabled(False)
        self.load_translations()

        self.engineer_mode_window.Recipe_Change_Signal.connect(self.Recipe_Change)
        # self.Recipe_Change()

        self.aoi_op_lead_time_start = datetime.now()
        self.aoi_op_lead_time_end = datetime.now()
    def debugBar(self, msg):
        self.statusBar().showMessage(str(msg), 5000)

    def IOCardConnect(self):
        self.IOCardThread.IOCard_connect()
        if self.IOCardThread.connect:
            self.debugBar('IOCard Connection!!!')
            self.IOCardThread.open()
            self.IOCardThread.start()
            # self.IOCardThread.rawdataINPUT.connect(self.showInput)
        else:
            self.debugBar('IOCard Disconnection!!!')

    def iniGuiEvent(self):
        self.pushButton_Start.clicked.connect(self.Start)
        self.pushButton_Reset.clicked.connect(self.Operate_stop)
        self.pushButton_24Hours.clicked.connect(self.Start24_Thread)
        self.timer.timeout.connect(self.updateCountdown)
        self.pushButton_TakeImage.clicked.connect(self.take_trainning_image)
        # self.modbus_reconnect_timer.timeout.connect(self.modbus_reconnect)
        # self.motor_idle_timer.timeout.connect(self.motor_idle)
        self.pushButton_Load_Recipe.clicked.connect(self.Load_recipe)
        self.pushButton_ReDetect.clicked.connect(self.Redetect)
        self.pushButton_Recipe_End.clicked.connect(self.Recipe_end)
        # self.engineer_mode_window.comboBox_recipe.currentIndexChanged.connect(self.Recipe_Change)
        self.login_window.pushButton_login.clicked.connect(self.Open_engineer_mode_Window)
        self.pushButton_engineer_mode.clicked.connect(self.Open_login_Window)
        self.engineer_mode_window.pushButton_TakeImage.clicked.connect(self.take_trainning_image)
        self.engineer_mode_window.pushButton_24Hours.clicked.connect(self.Start24_Thread)

    def Open_login_Window(self):
        self.login_window.show()
        
    def Open_engineer_mode_Window(self):
        if self.login_window.logIn() == True:
            self.engineer_mode_window.show()
            self.login_window.close()

        self.engineer_mode_window.checkBox_language_zh.clicked.connect(lambda: self.language_change('zh'))
        self.engineer_mode_window.checkBox_language_en.clicked.connect(lambda: self.language_change('en'))
        self.engineer_mode_window.checkBox_language_pt.clicked.connect(lambda: self.language_change('pt'))
        self.engineer_mode_window.checkBox_language_tv.clicked.connect(lambda: self.language_change('tv'))
    def load_translations(self):
        file_path = './i18n_language/translations.yaml'
        with open(file_path, 'r', encoding='utf-8') as file:
            self.translations = yaml.safe_load(file)
    def language_change(self, lang):
        _translate = QtCore.QCoreApplication.translate
        self.engineer_mode_window.label.setText(_translate("Screwdriver_Detection_EngineerMode_Window", self.translations.get(lang, {}).get('mode', "")))

        self.pushButton_Start.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_Start_Text', "")))
        self.pushButton_Reset.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_Reset_Text', "")))
        self.pushButton_ReDetect.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_ReDetect_Text', "")))
        self.pushButton_Load_Recipe.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_Load_Recipe_Text', "")))
        self.pushButton_Recipe_End.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_Recipe_End_Text', "")))
        self.pushButton_engineer_mode.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('pushButton_engineer_mode_Text', "")))

        self.label_workNumber.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_workNumber_Text', "")))
        self.label_workAmount.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_workAmount_Text', "")))
        self.label_partNumber.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_partNumber_Text', "")))
        self.label_partName.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_partName_Text', "")))
        self.label_workAmountReal.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_workAmountReal_Text', "")))
        self.label_NGAmount.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_NGAmount_Text', "")))
        self.label_passAmount.setText(_translate("Screwdriver_Detection_Window", self.translations.get(lang, {}).get('label_passAmount_Text', "")))


    def Recipe_Change(self):
        self.pushButton_Recipe_End.setEnabled(False)
        self.pushButton_Load_Recipe.setEnabled(False)
        self.pushButton_Start.setEnabled(False)
        self.pushButton_ReDetect.setEnabled(False)
        self.pushButton_24Hours.setEnabled(False)
        self.pushButton_Reset.setEnabled(False)
        self.pushButton_TakeImage.setEnabled(False)
        try:
            self.camera.Recipe_Change(self.engineer_mode_window.comboBox_recipe.currentText())

            if self.engineer_mode_window.comboBox_recipe.currentText() == 'Milwaukee':
                self.recipe_model = 'Milwaukee'

            elif self.engineer_mode_window.comboBox_recipe.currentText() == 'KleinTool':
                self.awm_Key_for_Recipe = 'M11-2303002'
                self.dbwindow.awm_key = 'M11-2303002'

            self.dev_logger.info(f'Recipe_Change {self.MYINI.recipe} --> {self.engineer_mode_window.comboBox_recipe.currentText()}')
            self.MYINI.recipe_change(self.engineer_mode_window.comboBox_recipe.currentText())
            threading.Thread(target=self.screwdrives_Object_Rebuild, args=()).start()
        except Exception as e:
            self.dev_logger.error(
                f'Recipe_Change {self.MYINI.recipe} --> {self.engineer_mode_window.comboBox_recipe.currentText()}\n{e}')
    def screwdrives_Object_Rebuild(self):
        print('screwdrives_Object_Rebuild start')
        self.screwdrives.clear()
        gc.collect()
        # print(f'self.MYINI.Identity_CodeName = {self.MYINI.Identity_CodeName}')
        for i, k in enumerate(self.MYINI.Identity_CodeName):
            # print(f'Identity_CodeName = {k}')
            sd = ScrewDrive(r".\model", self.dev_logger, k, myIni=self.MYINI)
            sd.report.connect(self.NG_Report)
            sd.status.connect(self.statusChange)
            self.screwdrives.append(sd)
        print(f'screwdrives_Object_Rebuild_len(self.screwdrives) = {len(self.screwdrives)}')
        self.pushButton_Recipe_End.setEnabled(True)
        # self.pushButton_Load_Recipe.setEnabled(True)
        self.pushButton_Start.setEnabled(True)
        self.pushButton_ReDetect.setEnabled(True)
        self.pushButton_24Hours.setEnabled(True)
        self.pushButton_Reset.setEnabled(True)
        self.pushButton_TakeImage.setEnabled(True)
        self.comboBox_recipe.setEnabled(True)

    def Redetect(self):
        self.dbwindow.database_isOpen = False
        self.dbwindow.isfirstchk = False
        self.pushButton_Start.click()
        self.real_detect_amount -= 1

    def Load_recipe(self):
        try:
            br = abfactory()
            br.process = CINO_S680
            br.setup_baudrate('COM5', '9600')
            br.turn_on_machine()
            readData = br.readData()
            self.dbwindow.awm_key = readData
            self.awm_Key_for_Recipe = readData
            print(f'br.readDate() = {self.dbwindow.awm_key}')
        except Exception as e: #沒有接掃碼器 跳meesengeBox

            self.dbwindow.awm_key = 'M11-2303001'
            self.awm_Key_for_Recipe = 'M11-2303001'
            print(f'barcodereader error --- {e}')
            
        try:
            read_datas = self.dbwindow.get_aoi_op_master_datas(self.dbwindow.awm_key)

            read_datas_weightname = self.dbwindow.get_aoi_recipe_master_datas(read_datas['part_no'])

            self.recipe_model = self.get_tool_name_from_ini(read_datas_weightname['para1'].split('.')[0])

            self.engineer_mode_window.comboBox_recipe.setCurrentText(self.recipe_model)
            # self.Recipe_Change()

            self.show_aoi_op_master_datas_on_UI(read_datas)

            self.pushButton_Load_Recipe.setEnabled(False)
            self.pushButton_Start.setEnabled(True)
            self.pushButton_ReDetect.setEnabled(True)
            self.pushButton_Recipe_End.setEnabled(True)
            self.pushButton_Recipe_End.setStyleSheet(
                'background-color: 	#4CAF50; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  # green
            self.pushButton_Load_Recipe.setStyleSheet(
                'background-color: 	#FF5555; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  # red

            time.sleep(1)

            self.aoi_op_lead_time_start = datetime.now()
            print(f'aoi_op_lead_time_start = {self.aoi_op_lead_time_start}')
        except Exception as e:
            self.dev_logger.error(f'Load_recipe\n{e}')
            self.showerror('工單讀取錯誤')

    # 定義函式，讀取INI檔並查找對應工具名稱
    def get_tool_name_from_ini(self, tool_id, ini_file='ScrewDrive.ini'):
        config = configparser.ConfigParser()
        config.read(ini_file)

        # 迭代RECIPE_Model下的所有項目，查找對應的ID
        for tool_name, id in config['RECIPE_Model'].items():
            if id == tool_id:
                # 將工具名稱的首字母變成大寫
                if tool_name == 'milwaukee':
                    tool_name = 'Milwaukee'
                elif tool_name == 'kleintool':
                    tool_name = 'KleinTool'
                elif tool_name == 'kleintoolblack':
                    tool_name = 'KleinToolblack'
                return tool_name
        return 'Milwaukee'
    def show_aoi_op_master_datas_on_UI(self, datas):
        # print(datas)
        self.label_ForRecipe_Change.setText(datas['awm_key'])
        self.label_prod_qty.setText(str(datas['prod_qty']))
        self.label_part_no.setText(datas['part_no'])
        self.label_item_name.setText(datas['part_name'])

    def Recipe_end(self):
        self.screwdrives.clear()
        gc.collect()
        self.pushButton_Recipe_End.setEnabled(False)
        self.pushButton_Start.setEnabled(False)
        self.pushButton_ReDetect.setEnabled(False)
        self.pushButton_Load_Recipe.setEnabled(True)
        self.pushButton_Load_Recipe.setStyleSheet(
            'background-color: 	#4CAF50; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  # green
        self.pushButton_Recipe_End.setStyleSheet(
            'background-color: 	#FF5555; border: 1px solid #dcdfe6; padding: 10px; border-radius: 20px;')  # red
        self.real_detect_amount = 0
        self.NG_Count = 0
        self.Start24_Count = 0

    def motor_idle(self):
        if self.IOCardThread.connect and self.pushButton_Start.accessibleName() == 'Start':
            self.IOCardThread.motor_idle_time += 1
            print('++++++++++1')
            if self.IOCardThread.motor_idle_time == 2:
                # self.motor_idle_timer.stop()
                self.pushButton_Start.setText('System Idle')
                self.pushButton_Start.setAccessibleName('System Idle')
                self.IOCardThread.motor_idle_time = 0
                self.moveMotorIn()
                print('Idle state start')

    def modbus_reconnect(self):
        self.modbus.modbus_reconnect_time += 1#1分鐘進來1次
        # print(f'閒置{self.modbus.modbus_reconnect_time}秒')
        if self.modbus.modbus_reconnect_time == 60 or self.modbus.Modbus_isOpen == False:#閒置1小時 或 重連失敗時 重新連線
            # print(f'重新連線了')
            self.modbus.close_connection()
            self.modbus.CloseModbus = True
            time.sleep(3)
            self.modbus = Modbus(dev_logger=self.dev_logger)
            self.dev_logger.info('modbus_reconnect')

    def iniLogging(self):
        logging_FileName = time.strftime('%Y%m%d')

        self.dev_logger: logging.Logger = logging.getLogger(name='dev')
        self.dev_logger.setLevel(logging.DEBUG)

        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        self.dev_logger.addHandler(handler)

        file_handler: logging.FileHandler = logging.FileHandler(rf'.\Logging\{logging_FileName}_dev.log', mode='a')
        file_handler.setFormatter(formatter)
        self.dev_logger.addHandler(file_handler)

    def closeEvent(self, event):
        print('window close')
        self.dev_logger.info('window closing')
        self.is_Timeup = False
        self.moveMotorIn()
        time.sleep(0.3)
        self.IOCardThread.closeAll()
        self.dev_logger.info('window closed')
        QApplication.closeAllWindows()

    def Operate_stop(self):
        time.sleep(0.3)
        # self.motor.Yellow()
        self.IOCardThread.openYellowLight_closeDetctLight()

    def DetectNG(self):
        time.sleep(0.3)
        # self.motor.Red()
        self.IOCardThread.openRedLight_closeDetctLight()
        if self.engineer_mode_window.checkBox_buzzerOn.isChecked() == True:
            time.sleep(0.5)
            # self.motor.Buzzer()
            self.IOCardThread.detectEndNG()

    def DetectOK(self):
        time.sleep(0.3)
        # self.motor.Green()
        self.IOCardThread.openYellowLight_closeDetctLight()

    def moveMotorOut(self):
        print('moveMotorForward')
        self.IOCardThread.updataDisSpeed(310, 400)#出來
    def moveMotorIn(self):
        print('moveMotorBackward')
        self.IOCardThread.updataDisSpeed(-310, 400)#進去
    def AI_Light(self):
        self.IOCardThread.detectStart_1()

    def AI_Light_Kleintools(self):
        self.modbus.com1_on()
        self.modbus.com2andcom3_on()
    def AOI_Light(self):
        self.IOCardThread.detectStart_2()

    def updateCountdown(self):
        hours, remainder = divmod(self.countdown_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_str = f'{hours} H {minutes} M {seconds} S'
        self.pushButton_24Hours.setText(time_str)

        self.countdown_seconds -= 1
        if self.countdown_seconds % 3600 == 0:
            print('self.countdown_seconds % 3600 == 0:')
        if self.countdown_seconds < 0:
            self.timer.stop()
            self.is_Timeup = False
            self.pushButton_24Hours.setText('倒數結束')
    def take_trainning_image(self):
        try:
            if os.path.exists(f'{self.engineer_mode_window.takeImage_file_route}') == True:
                print(self.engineer_mode_window.takeImage_file_route)
                self.Time_for_Record_ForSaveKleinTool = time.strftime('%Y%m%d_%H%M%S')
                threading.Thread(target=self.take_trainning_image_Thread, args=()).start()
            else:
                self.engineer_mode_window.takeImage_file_route = ''
                self.showerror('取像路徑錯誤')

        except:
            self.engineer_mode_window.takeImage_file_route = ''
            self.showerror('取像路徑錯誤')

    def showerror(self, hintMessage):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title='error', message=hintMessage)

    def take_trainning_image_Thread(self):
        # self.move()
        self.moveMotorIn()
        self.AI_Light()
        # self.AI_Light_Kleintools()
        time.sleep(1.5)
        self.engineer_mode_window.label_OK.setText('Taking Image')
        self.engineer_mode_window.label_OK.setStyleSheet(
            'background-color: 	#272727; color: white; border-radius: 5px; padding: 10px; font-size: 36px;')

        for exp_time in self.exposure_time_tuple_AI:
            threading.Thread(target=self.camera.SetExposureTime, args=(float(exp_time),)).start()
            time.sleep(0.4)

            self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
            self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)
            cv2.imwrite(f'{self.engineer_mode_window.takeImage_file_route}/AI/{self.Time_for_Record_ForSaveKleinTool}_AI_{exp_time}.png',
                        cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY))

        self.AOI_Light()
        time.sleep(0.15)
        for exp_time in self.exposure_time_tuple_AOI:
            threading.Thread(target=self.camera.SetExposureTime, args=(float(exp_time),)).start()
            time.sleep(0.4)

            self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
            self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)
            cv2.imwrite(f'{self.engineer_mode_window.takeImage_file_route}/AOI/{self.Time_for_Record_ForSaveKleinTool}_AOI_{exp_time}.png',
                        cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY))

        self.After_CameraGrab()
        self.engineer_mode_window.label_OK.setText('Finish')
        self.engineer_mode_window.label_OK.setStyleSheet(
            'background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; font-size: 36px;')

    def Start24_Thread(self):
        if self.is_Timeup == False:
            self.NG_Count = 0
            self.Start24_Count = 0
            self.pushButton_Start.setEnabled(False)
            self.countdown_seconds = 24 * 60 * 60  # 設定倒數秒數，這裡是 24 小時的秒數
            self.timer.start(1000)  # 設定定時器每秒觸發一次
            self.is_Timeup = True
            threading.Thread(target=self.Start24, args=()).start()
        else:
            self.is_Timeup = False
            self.timer.stop()
            self.pushButton_Start.setEnabled(True)

    def Start24(self):
        # now = datetime.now()
        # later = now + timedelta(hours=24)
        while self.is_Timeup:
            # self.move()
            self.moveMotorIn()
            while not self.IOCardThread.MOTORSTATE[1]:
                time.sleep(0.01)
            self.AI_Light()
            time.sleep(1)
            self.label_OK.setText('calculating')
            self.dbwindow.reset_data(self.awm_Key_for_Recipe)
            self.dbwindow.creat_Serial_Number()
            self.dbwindow.aoi_start = datetime.now()
            self.starttime_ALLTIME = time.time()
            # print(f' ------------------------------------TimeStart --> {time.time()} ------------------------------------')
            self.All_AIPass = True
            self.All_Report_count = 0
            self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
            threading.Thread(target=self.camera.SetExposureTime, args=(self.MYINI.Camera_Setting['exposuretime_aoi'],)).start()
            self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)
            for sd in self.screwdrives:
                sd.Result = self.Result
                sd.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
                sd.Main(1, self.dbwindow.aoi_start)
            # self.screwdrive.Result = self.Result
            # self.screwdrive.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
            # self.screwdrive.Main(1, self.dbwindow.aoi_start)
            starttime = time.time()
            # self.camera.SetExposureTime(float(100000))
            self.AOI_Light()
            time.sleep(0.25)
            # cv2.imwrite(f'./AI.png', self.screwdrive.image_AI)
            for sd in self.screwdrives:
                sd.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1), cv2.COLOR_BGR2GRAY)
                sd.AOIimage_ISREADY = True
            # self.screwdrive.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1),
            #                                          cv2.COLOR_BGR2GRAY)
            # self.screwdrive.AOIimage_ISREADY = True
            # cv2.imwrite(f'./AOI.png', self.screwdrive.image_AOI)
            print(f'!!拍攝AOI影像 : {time.time() - starttime}')
            self.After_CameraGrab()
            # threading.Thread(target=self.After_CameraGrab, args=()).start()

            time.sleep(6)

    def Start(self):
        # if self.awm_Key_for_Recipe == 'M11-2303001' and self.dbwindow.awm_key == 'M11-2303001':
        # print(self.awm_Key_for_Recipe)

        if self.recipe_model == 'Milwaukee':
            threading.Thread(target=self.Start_Thread_Milwaukee, args=()).start()
        if self.awm_Key_for_Recipe == 'M11-2303002':
            threading.Thread(target=self.Start_Thread_KleinTools_Gray, args=()).start()
        self.real_detect_amount += 1
    def Start_Thread_Milwaukee(self):
        if self.pushButton_Start.text() == 'System Idle':
            # self.motor_idle_timer.start(5000)
            self.moveMotorOut()
            self.pushButton_Start.setText('Start')
            self.pushButton_Start.setAccessibleName('Start')

            print('Motor idle over')
        else:
            self.label_OK.setText('calculating')
            self.pushButton_Start.setEnabled(False)
            self.pushButton_ReDetect.setEnabled(False)
            # self.move()
            self.moveMotorIn()
            time.sleep(0.1)
            while not self.IOCardThread.MOTORSTATE[1]:
                time.sleep(0.1)
                # print(f'self.IOCardThread.MOTORSTATE = {self.IOCardThread.MOTORSTATE}')
            self.AI_Light()
            time.sleep(0.6)
            self.dbwindow.reset_data(self.awm_Key_for_Recipe)
            self.dbwindow.creat_Serial_Number()
            self.dbwindow.aoi_start = datetime.now()
            self.starttime_ALLTIME = time.time()
            # print(f' ------------------------------------TimeStart --> {time.time()} ------------------------------------')
            self.All_AIPass = True
            self.All_Report_count = 0
            self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
            threading.Thread(target=self.camera.SetExposureTime, args=(self.MYINI.Camera_Setting['exposuretime_aoi'],)).start()
            self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)
            for sd in self.screwdrives:
                sd.Result = self.Result
                sd.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
                sd.Main(1, self.dbwindow.aoi_start)
            # self.screwdrive.Result = self.Result
            # self.screwdrive.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
            # self.screwdrive.Main(1, self.dbwindow.aoi_start)
            starttime = time.time()
            # self.camera.SetExposureTime(float(100000))
            self.AOI_Light()
            time.sleep(0.15)
            # cv2.imwrite(f'./AI.png', self.screwdrive.image_AI)
            for sd in self.screwdrives:
                sd.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1), cv2.COLOR_BGR2GRAY)
                sd.AOIimage_ISREADY = True
            # self.screwdrive.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1),
            #                                          cv2.COLOR_BGR2GRAY)
            # self.screwdrive.AOIimage_ISREADY = True
            # cv2.imwrite(f'./AOI.png', self.screwdrive.image_AOI)
            print(f'!!拍攝AOI影像 : {time.time() - starttime}')
            self.After_CameraGrab()
            # threading.Thread(target=self.After_CameraGrab, args=()).start()
    def Start_Thread_KleinTools_Gray(self):
        if self.pushButton_Start.text() == 'System Idle':
            # self.motor_idle_timer.start(5000)
            self.moveMotorOut()
            self.pushButton_Start.setText('Start')
            self.pushButton_Start.setAccessibleName('Start')

            print('Motor idle over')
        else:
            self.label_OK.setText('calculating')
            self.pushButton_Start.setEnabled(False)
            self.pushButton_ReDetect.setEnabled(False)
            # self.move()
            self.moveMotorIn()
            threading.Thread(target=self.camera.SetExposureTime, args=(self.MYINI.Camera_Setting['exposuretime_aoi'],)).start()
            time.sleep(0.1)
            while not self.IOCardThread.MOTORSTATE[1]:
                time.sleep(0.1)
                # print(f'self.IOCardThread.MOTORSTATE = {self.IOCardThread.MOTORSTATE}')
            self.AOI_Light()
            time.sleep(0.6)
            self.dbwindow.reset_data(self.awm_Key_for_Recipe)
            self.dbwindow.creat_Serial_Number()
            self.dbwindow.aoi_start = datetime.now()
            self.starttime_ALLTIME = time.time()
            # print(f' ------------------------------------TimeStart --> {time.time()} ------------------------------------')
            self.All_AIPass = True
            self.All_Report_count = 0
            self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
            self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)

            for sd in self.screwdrives:
                sd.Result = self.Result
                sd.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
                # cv2.imwrite(f'./AI.png', sd.image_AI)
                sd.Main(1, self.dbwindow.aoi_start)
            # self.screwdrive.Result = self.Result
            # self.screwdrive.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
            # self.screwdrive.Main(1, self.dbwindow.aoi_start)
            starttime = time.time()
            # self.camera.SetExposureTime(float(100000))
            time.sleep(0.15)
            # cv2.imwrite(f'./AI.png', self.screwdrive.image_AI)
            for sd in self.screwdrives:
                # sd.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1), cv2.COLOR_BGR2GRAY)
                sd.image_AOI = copy.deepcopy(cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY))
                # cv2.imwrite(f'./AOI.png', sd.image_AOI)
                sd.AOIimage_ISREADY = True
            # self.screwdrive.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1),
            #                                          cv2.COLOR_BGR2GRAY)
            # self.screwdrive.AOIimage_ISREADY = True
            # cv2.imwrite(f'./AOI.png', self.screwdrive.image_AOI)
            print(f'!!拍攝AOI影像 : {time.time() - starttime}')
            self.After_CameraGrab()
            # threading.Thread(target=self.After_CameraGrab, args=()).start()

    def After_CameraGrab(self):
        # self.move()
        self.moveMotorOut()
        time.sleep(0.2)

        self.camera.SetExposureTime(self.MYINI.Camera_Setting['exposuretime_ai'])

        # if self.modbus.com1_Status:
        #     self.modbus.com1_off()
        #     self.modbus.com1_Status = not self.modbus.com1_Status
    def statusChange(self, statusNow):
        # if self.All_AIPass or self.checkBox_saveImage.isChecked():
        #     output_file_name = f'{self.camera.cam.ExposureTime.GetValue()}.png'
        #     output_file_path = fr"D:\ScrewdriverFile\ScrewdriverImage\0922\{output_file_name}"
        #     cv2.imwrite(output_file_path, self.inputimage)
        if statusNow:
            start = time.time()
            self.imageLable_Show(self.label_Image, cv2.rotate(self.Result, cv2.ROTATE_90_CLOCKWISE))
            end = time.time()
            print(f'!!顯示影像 : {end - start:.8f}')
            self.dbwindow.aoi_end = datetime.now()
            print(f'!!ALLTIME : {time.time() - self.starttime_ALLTIME}')
            starttime = time.time()
            if self.All_Report_count == len(self.MYINI.Class_Name_All) * len(self.MYINI.Identity_CodeName):
                # print(f'QQQQQQ:{self.aoi_op_lead_time_end} - {self.aoi_op_lead_time_start}')
                self.aoi_op_lead_time_end = self.dbwindow.aoi_end
                # print(f'QQQQQQ:{self.aoi_op_lead_time_end} - {self.aoi_op_lead_time_start}')
                self.dbwindow.aoi_op_lead_time = str((self.aoi_op_lead_time_end - self.aoi_op_lead_time_start).total_seconds())
                # print(f'{self.dbwindow.aoi_op_lead_time} = {self.aoi_op_lead_time_end} - {self.aoi_op_lead_time_start}')
                self.aoi_op_lead_time_start = self.aoi_op_lead_time_end

                self.dbwindow.write_data()
                self.dbwindow.database_isOpen = True

                time.sleep(0.5)
                self.pushButton_Start.setEnabled(True)
                self.pushButton_ReDetect.setEnabled(True)
            endtime = time.time()
            print(f'!!上傳資料庫 : {endtime - starttime}')
            print(f'********************結束********************')


    def NG_Report(self, is_OK, confidence, Index):
        try:
            self.All_Report(is_OK, confidence, Index)
            # self.imageLable_Show(self.label_image_Result, self.Result)

            if is_OK == 0:#AI False
                self.All_AIPass = False
        except Exception as e:
            self.dev_logger.error(e)

    def All_Report(self, is_OK, confidence, Index):
        if not (is_OK in [1]):
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.ng_bits_index = self.All_Report_count + 1
            else:
                self.dbwindow.ng_bits_index = f'{self.dbwindow.ng_bits_index},{self.All_Report_count + 1}'

        self.All_Report_count += 1

        if self.All_Report_count == len(self.MYINI.Class_Name_All) * len(self.MYINI.Identity_CodeName):
            self.Start24_Count += 1
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.pass_or_failure = True
                self.DetectOK()
                self.label_OK.setText('OK')
                self.label_OK.setStyleSheet(
                    'background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; font-size: 36px;')
                self.passdetect_amount += 1 #合格數量+1
                self.label_passdetect_amount.setText(f'{self.passdetect_amount}')

            elif len([x for x in self.screwdrives[0].NG_Image_Information.values() if 'slotted' in x]) > 12 and len(
                    [x for x in self.screwdrives[0].NG_Image_Information.values() if 'vacancy' in x]) > 12:
                self.dbwindow.ng_bits_index = ''
                self.dbwindow.pass_or_failure = True
                self.DetectNG()
                self.label_OK.setText('不計數')
                self.label_OK.setStyleSheet(
                    'background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; font-size: 36px;')
            else:
                self.NG_Count += 1
                try:
                    ng_bits_index_amount = len(self.dbwindow.ng_bits_index.split(","))
                    self.label_OK.setText(f'NG    {ng_bits_index_amount}')
                except Exception as e:
                    self.label_OK.setText(f'NG    1')
                    print(e)
                self.label_OK.setStyleSheet(
                    'background-color: #FF5555; color: white; border-radius: 5px; padding: 10px; font-size: 36px;')
                self.DetectNG()
            self.lineEdit_NG_Count.setText(f'NG : {self.NG_Count} / {self.Start24_Count}')

            self.label_detect_amount.setText(f'{self.real_detect_amount}')
            # else:
            #     formatted_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                # cv2.imwrite(f'./Defect AI Image/{formatted_time}.png', self.Result)
    def imageLable_Show(self, image_label, Show_image):
        Show_image = cv2.cvtColor(Show_image, cv2.COLOR_BGR2RGB)  # 圖像存儲使用8-8-8 24位RGB格式
        rows, cols, channels = Show_image.shape  # 獲取圖片長寬
        QImg = QImage(Show_image.data, cols, rows, cols*channels, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = Screwdriver_Detection()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
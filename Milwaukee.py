import copy
import threading
import time
from datetime import datetime
import sys
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableWidgetItem, QHeaderView, QWidget
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from Main import Ui_MainWindow
from ScrewDrive import ScrewDrive
from Camera import Camera
from Modbus import Modbus
from Screwdriver_Database import DB_MainWindow
from Motor import Motor
from ROI_Window.ROI import ROIWindow
import logging
from Myini import Myini
# pip install -r C:\Users\YC03SRA003\Desktop\0507ProgramBackup\package_new.txt

'''
pip install psycopg2
pip install pyserial 
pip install SerialPort
pip install pypylon
pip install PyQt5 
'''

class Main_Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        self.setupUi(self)
        self.iniLogging()
        self.dev_logger.info('Program Start')
        self.iniGuiEvent()
        self.label_image_Main.setScaledContents(True)
        self.label_image_Result.setScaledContents(True)
        self.MYINI = Myini()
        self.motor = Motor()
        if self.motor.Motor_isOpen == False:
            self.pushButton_MotorMove.setEnabled(False)
            self.pushButton_MotorMove.setText('馬達未連線')
            self.pushButton_MotorMove.setStyleSheet('color: red')
            self.pushButton_MotorMove.setEnabled(False)
        # self.serialPort = SerialPort()
        self.modbus = Modbus(self.dev_logger)
        if self.modbus.Modbus_isOpen is False:
            self.pushButton_Light_Control.setEnabled(False)
            self.pushButton_Light_Control.setText('IO卡未連線')
            self.pushButton_Light_Control.setStyleSheet('color: red')
        # self.screwdrive = ScrewDrive(r".\model")
        # self.screwdrive = ScrewDrive(r".\models")

        # self.screwdrive.report.connect(self.NG_Report)
        # self.screwdrive.output_finish.connect(self.receive_output_message_Finish)
        # self.screwdrive.status.connect(self.statusChange)

        # self.Identity = ['alpha', 'beta', 'gamma', 'delta']
        self.screwdrives = list()
        for i, k in enumerate(self.MYINI.Identity_CodeName):
            sd = ScrewDrive(r".\model", self.dev_logger, k, myIni=self.MYINI)
            sd.report.connect(self.NG_Report)
            sd.status.connect(self.statusChange)

            sd.output_finish.connect(self.receive_output_message_Finish)
            self.screwdrives.append(sd)


        self.tableWidget_OutputMessage.setColumnCount(4)
        self.tableWidget_OutputMessage.setRowCount(10)
        self.tableWidget_OutputMessage.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_OutputMessage.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tableWidget_OutputMessage_AllResult.setColumnCount(7)
        self.tableWidget_OutputMessage_AllResult.setRowCount(10)
        self.tableWidget_OutputMessage_AllResult.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_OutputMessage_AllResult.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.camera = Camera()
        if self.camera.Camera_isOpen:
            self.camera.FreeRun.connect(self.freerun)
        else:
            self.pushButton_cameralink.setEnabled(False)
            self.pushButton_cameralink.setText('相機未連線')
            self.pushButton_cameralink.setStyleSheet('color: red')
            self.pushButton_Grab.setEnabled(False)
        self.comboBox_recipe.addItems([recipe for recipe in self.MYINI.recipes])

        # self.AI_Light()
        self.dbwindow = DB_MainWindow()
        self.pushButton_Grab.setEnabled(False)
        self.Operate_stop()
        # self.ExposureTimeTuple = (46103, 48103, 50103, 52103, 54103)
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
    def iniGuiEvent(self):
        self.pushButton_Seach.clicked.connect(self.Main)
        self.pushButton_cameralink.clicked.connect(self.CameraLink)
        self.pushButton_Grab.clicked.connect(self.CameraGrab)
        self.pushButton_ROIWindow.clicked.connect(self.Open_ROIWindow)
        self.pushButton_Database_Window.clicked.connect(self.Open_DBWindow)
        self.horizontalSlider_ExposureTime.valueChanged.connect(self.WantToCreateExposureTime)
        self.pushButton_Light_Control.clicked.connect(self.IO_Control)
        self.pushButton_MotorMove.clicked.connect(self.motorGO)
        self.pushButton_NGReset.clicked.connect(self.Operate_stop)
        self.comboBox_recipe.currentIndexChanged.connect(self.Recipe_Change)

    def Recipe_Change(self):
        try:
            self.camera.Recipe_Change(self.comboBox_recipe.currentText())
            self.dev_logger.info(f'Recipe_Change {self.MYINI.recipe} --> {self.comboBox_recipe.currentText()}')
            self.MYINI.recipe_change(self.comboBox_recipe.currentText())
            self.screwdrives.clear()
            for i, k in enumerate(self.MYINI.Identity_CodeName):
                sd = ScrewDrive(r".\model", self.dev_logger, k, myIni=self.MYINI)
                sd.report.connect(self.NG_Report)
                sd.status.connect(self.statusChange)
                sd.output_finish.connect(self.receive_output_message_Finish)
                self.screwdrives.append(sd)
        except Exception as e:
            self.dev_logger.error(
                f'Recipe_Change {self.MYINI.recipe} --> {self.comboBox_recipe.currentText()}\n{e}')

    def motorGO(self):
        if self.motor.Motor_isOpen:
            self.motor.Move()
    def Operate_start(self):
        if self.motor.Motor_isOpen:
            self.motor.Off()
            self.motor.Green()
    def Operate_stop(self):
        if self.motor.Motor_isOpen:
            self.motor.Off()
            self.motor.Yellow()
    def DetectNG(self):
        if self.motor.Motor_isOpen:
            self.motor.Off()
            # self.motor.Buzzer()
            self.motor.Red()
    def IO_Control(self):
        if self.pushButton_Light_Control.text() == 'AOILight':
            self.AOI_Light()
            self.pushButton_Light_Control.setText('AILight')
        else:
            self.AI_Light()
            self.pushButton_Light_Control.setText('AOILight')
    def AI_Light(self):
        # self.horizontalSlider_ExposureTime.setValue(40000)
        if self.modbus.Modbus_isOpen:
            if self.modbus.com1_Status:
                self.modbus.com1_off()
                self.modbus.com1_Status = not self.modbus.com1_Status
            if self.modbus.com2andcom3_Status is False:
                self.modbus.com2andcom3_on()
                self.modbus.com2andcom3_Status = not self.modbus.com2andcom3_Status
    def AOI_Light(self):
        # self.horizontalSlider_ExposureTime.setValue(25000)
        if self.modbus.Modbus_isOpen:
            if self.modbus.com2andcom3_Status:
                self.modbus.com2andcom3_off()
                self.modbus.com2andcom3_Status = not self.modbus.com2andcom3_Status
            if self.modbus.com1_Status is False:
                self.modbus.com1_on()
                self.modbus.com1_Status = not self.modbus.com1_Status
    def Open_ROIWindow(self):
        self.roiwindow = ROIWindow(self.camera, self.screwdrives[0], self.motor, self.MYINI)
        self.roiwindow.show()
    def Open_DBWindow(self):
        self.dbwindow.show()
    def closeEvent(self, event):
        QApplication.closeAllWindows()
        print('MainWindow was closed')
        self.motor.Off()
        self.modbus.com_all_off()
        self.motor.Motor_isForwards = True
        self.motor.Move()
    def WantToCreateExposureTime(self):
        self.camera.SetExposureTime(float(self.horizontalSlider_ExposureTime.value()))
        self.label_ExposureTime.setText(str(self.horizontalSlider_ExposureTime.value()))
    def CameraLink(self):
        self.camera.start()
        self.pushButton_cameralink.setEnabled(False)
        self.pushButton_Grab.setEnabled(True)

    def CameraGrab(self):
        self.Operate_start()
        self.motorGO()
        self.AI_Light()
        time.sleep(1)
        self.label_status.setText('calculating')
        self.dbwindow.reset_data()
        self.dbwindow.creat_Serial_Number()
        self.dbwindow.aoi_start = datetime.now()
        self.starttime_ALLTIME = time.time()

        self.tableWidget_OutputMessage.clear()
        self.tableWidget_OutputMessage_AllResult.clear()
        self.messages_Finish_count = 0

        self.All_AIPass = True
        self.All_Report_count = 0
        self.inputimage = copy.deepcopy(self.camera.Image_RealTime)
        threading.Thread(target=self.camera.SetExposureTime, args=(self.MYINI.Camera_Setting['exposuretime_aoi'],)).start()
        self.Result = cv2.flip(copy.deepcopy(self.inputimage), 1)
        for sd in self.screwdrives:
            sd.Result = self.Result
            sd.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
            sd.Main(1, self.dbwindow.aoi_start)
        # self.camera.SetExposureTime(float(100000))
        self.AOI_Light()
        time.sleep(0.15)
        # cv2.imwrite(rf'./AI.png', self.screwdrive.image_AI)
        for sd in self.screwdrives:
            sd.image_AOI = cv2.cvtColor(cv2.flip(copy.deepcopy(self.camera.Image_RealTime), 1), cv2.COLOR_BGR2GRAY)
            sd.AOIimage_ISREADY = True
        print(f'!!AOI拍照時間 : {time.time() - self.starttime_ALLTIME}')

        # cv2.imwrite(rf'./AOI.png', self.screwdrive.image_AOI)
        # self.horizontalSlider_ExposureTime.setValue(27000)
        threading.Thread(target=self.After_CameraGrab, args=()).start()


    def After_CameraGrab(self):
        self.motorGO()
        self.camera.SetExposureTime(self.MYINI.Camera_Setting['exposuretime_ai'])
        if self.modbus.com1_Status:
            self.modbus.com1_off()
            self.modbus.com1_Status = not self.modbus.com1_Status
    def freerun(self):
        image = self.camera.Image_RealTime
        self.imageLable_Show(self.label_image_Main, image)
    def Seach(self):
        for i in range(0, 2):
            filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', r'D:\ScrewdriverFile\ScrewdriverImage', 'Image Files(*.png *.jpg *.bmp *.jpeg)')
            self.inputimage_filename = filename
            if filename:
                try:
                    self.inputimage = cv2.imread(filename, cv2.IMREAD_COLOR)
                    # self.inputimage = self.rotate_and_mirror(self.inputimage)
                    if i == 0:
                        self.Result = cv2.flip(self.inputimage, 1)
                        self.screwdrive.Result = self.Result
                        # self.inputimage = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), -1)
                        self.imageLable_Show(self.label_image_Main, self.inputimage)
                    elif i == 1:
                        self.Result_2 = cv2.flip(self.inputimage, 1)
                        self.Result_2 = cv2.cvtColor(self.Result_2, cv2.COLOR_BGR2GRAY)

                except BaseException as e:
                    print('openFiles:', e)
    def Main(self):
        self.label_status.setText('caculating')
        self.dbwindow.reset_data()
        self.dbwindow.creat_Serial_Number()
        self.dbwindow.aoi_start = datetime.now()
        self.Seach()
        self.tableWidget_OutputMessage.clear()
        self.tableWidget_OutputMessage_AllResult.clear()
        self.All_Report_count = 0
        self.All_AIPass = True
        Result_Gray = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
        self.screwdrive.Main(1)
        self.messages_Finish_count = 0
    def NG_Report(self, is_OK, confidence, Index, diameter, numberofvertices):
        item = QTableWidgetItem(self.MYINI.Class_Name_All[Index])
        self.tableWidget_OutputMessage_AllResult.setItem(self.All_Report_count, 0, item)
        if is_OK == 1:
            item = QTableWidgetItem('正確')
        else:
            if is_OK == 404:
                item = QTableWidgetItem('NotValid')
                item.setBackground(QColor(29, 230, 181))
            else:
                item = QTableWidgetItem('錯誤')
                item.setBackground(QColor(254, 142, 109))
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.ng_bits_index = self.All_Report_count + 1
            else:
                self.dbwindow.ng_bits_index = f'{self.dbwindow.ng_bits_index},{self.All_Report_count + 1}'

        self.tableWidget_OutputMessage_AllResult.setItem(self.All_Report_count, 1, item)
        confidences = confidence.split(',')
        for i, cf in enumerate(confidences):
            item = QTableWidgetItem(cf)
            self.tableWidget_OutputMessage_AllResult.setItem(self.All_Report_count, 2 + i, item)
        item = QTableWidgetItem(diameter)
        self.tableWidget_OutputMessage_AllResult.setItem(self.All_Report_count, 3, item)
        item = QTableWidgetItem(numberofvertices)
        self.tableWidget_OutputMessage_AllResult.setItem(self.All_Report_count, 4, item)

        self.All_Report_count += 1
        self.tableWidget_OutputMessage_AllResult.setRowCount(self.All_Report_count + 1)

        if self.All_Report_count == len(self.MYINI.Class_Name_All):
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.pass_or_failure = True
                self.Operate_stop()
            else:
                self.DetectNG()
                formatted_time = self.dbwindow.aoi_start.strftime('%Y%m%d_%H%M%S')
                cv2.imwrite(f'./Defect AI Image/{formatted_time}.png', self.Result)
        if is_OK == 0:#AI False
            self.All_AIPass = False
    def statusChange(self, statusNow):
        # if self.All_AIPass or self.checkBox_saveImage.isChecked():
        #     output_file_name = f'{self.camera.cam.ExposureTime.GetValue()}.png'
        #     output_file_path = fr"D:\ScrewdriverFile\ScrewdriverImage\0922\{output_file_name}"
        #     cv2.imwrite(output_file_path, self.inputimage)
        print('statusChange')
        if statusNow:
            self.imageLable_Show(self.label_image_Result, self.Result)
            self.label_status.setText('end')
            self.dbwindow.aoi_end = datetime.now()
            print(f'!!ALLTIME : {time.time() - self.starttime_ALLTIME}')
            starttime = time.time()
            self.dbwindow.write_data()
            endtime = time.time()
            print(f'!!上傳資料庫 : {endtime - starttime}')
            print(f'********************結束********************')


    def imageLable_Show(self, image_label, Show_image):
        Show_image = cv2.cvtColor(Show_image, cv2.COLOR_BGR2RGB)  # 圖像存儲使用8-8-8 24位RGB格式
        rows, cols, channels = Show_image.shape  # 獲取圖片長寬
        QImg = QImage(Show_image.data, cols, rows, cols*channels, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        image_label.setPixmap(pixmap)

    def rotate_and_mirror(self, input_image):
        # 進行順時針旋轉90度
        rotated_img = cv2.rotate(input_image, cv2.ROTATE_90_CLOCKWISE)
        # 沿著Y軸鏡射
        mirrored_img = cv2.flip(rotated_img, 1)
        return mirrored_img
    def receive_output_message_Finish(self, image_number, type, succese, failure_type):
        item = QTableWidgetItem(image_number)
        self.tableWidget_OutputMessage.setItem(self.messages_Finish_count, 0, item)
        item = QTableWidgetItem(type)
        self.tableWidget_OutputMessage.setItem(self.messages_Finish_count, 1, item)
        item = QTableWidgetItem(succese)
        self.tableWidget_OutputMessage.setItem(self.messages_Finish_count, 2, item)
        item = QTableWidgetItem(failure_type)
        self.tableWidget_OutputMessage.setItem(self.messages_Finish_count, 3, item)

        self.messages_Finish_count += 1
        self.tableWidget_OutputMessage.setRowCount(self.messages_Finish_count+1)


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = Main_Window()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
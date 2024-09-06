import copy
import threading
from datetime import datetime, timedelta
import re
import time
import PyQt5
import numpy as np
import os
import sys
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableWidgetItem, QHeaderView, QGraphicsScene, \
    QGraphicsPixmapItem, QGraphicsRectItem
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from screwdriver_test_Window import Ui_MainWindow
from ScrewDrive import ScrewDrive
from ScrewDrive import Measure
import logging
from Myini import Myini
"""
python 3.6
pip install tensorflow-gpu==2.6.0
pip install keras==2.6.0
pip install opencv-python==3.4.2.16
pip install matplotlib==3.3.4
"""

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QObject):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # 創建主界面對象
        self.setupUi(self)
        #self.imageLable.setScaledContents(True)
        #self.imageLable_2.setScaledContents(True)
        self.iniLogging()
        self.dev_logger.info('screwdriver_test --> Start')
        self.MYINI = Myini()
        self.comboBox_recipe.addItems([recipe for recipe in self.MYINI.recipes])
        # self.dbwindow = DB_MainWindow()
        self.label_Image.setScaledContents(True)
        self.iniGuiEvent()
        self.tableWidget_information.setColumnCount(4)
        self.tableWidget_information.setRowCount(10)
        self.label_image_information.setScaledContents(True)
        self.label_image_histogram.setScaledContents(True)
        self.label_image_Remedy.setScaledContents(True)
        self.label_image_extend.setScaledContents(True)
        self.tableWidget_information_correctrate.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_information_correctrate.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tableWidget_information.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.tableWidget_information.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget_information.setSortingEnabled(True)
        # self.tableWidget_information.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.comboBox_models.addItems(os.listdir(r'D:\ScrewdriverFile\model\0509\13'))
        self.comboBox_Validation_set.addItems(os.listdir(r'D:\ScrewdriverFile\ScrewdriverImage\Varification'))
        self.ClassNumber = 0
        self.inputimage_filename = ''
        # self.screwdrive.eventManager.AddEventListener(self.screwdrive.EVENT_ARTICAL, )
        # self.screwdrive.eventManager.Start()
        self.screwdrive = ScrewDrive(dev_logger=self.dev_logger, myIni=self.MYINI)
        self.screwdrive.trigger.connect(self.receive_message)
        self.screwdrive.finish.connect(self.receive_message_Finish)
        self.screwdrive.Measure_Step.connect(self.measure_step)
        self.screwDrive_for_test  = ScrewDrive_For_Test(myIni=self.MYINI)
        self.screwDrive_for_test.trigger.connect(self.receive_message)
        self.screwDrive_for_test.finish.connect(self.receive_message_Finish)
    def iniGuiEvent(self):
        self.comboBox_recipe.currentIndexChanged.connect(self.Recipe_Change)
        self.btn_testmain.clicked.connect(self.Main)
        self.btn_testmeasure.clicked.connect(self.Test_Measure)
        self.btn_Measure.clicked.connect(self.Measure)
        self.btn_softwareTest.clicked.connect(self.softwareTest)
        self.tableWidget_information.cellClicked.connect(self.ShowImage)
        self.comboBox_AI_Class.currentIndexChanged.connect(self.AI_Class_Changed)

    def iniLogging(self):
        logging_FileName = time.strftime('%Y%m%d')

        self.dev_logger: logging.Logger = logging.getLogger(name='dev')
        self.dev_logger.setLevel(logging.DEBUG)

        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        self.dev_logger.addHandler(handler)

        file_handler: logging.FileHandler = logging.FileHandler(rf'.\Logging\screwdriver_test\{logging_FileName}_dev.log', mode='a')
        file_handler.setFormatter(formatter)
        self.dev_logger.addHandler(file_handler)

    def Recipe_Change(self):
        try:
            self.MYINI.recipe_change(self.comboBox_recipe.currentText())
            self.dev_logger.info(f'Recipe_Change {self.MYINI.recipe} --> {self.comboBox_recipe.currentText()}')
        except Exception as e:
            self.dev_logger.error(f'Recipe_Change {self.MYINI.recipe} --> {self.comboBox_recipe.currentText()}\n{e}')



    def softwareTest(self):
        self.dbwindow.reset_data()
        self.dbwindow.creat_Serial_Number()
        self.dbwindow.aoi_start = datetime.now()
        self.screwdrive = ScrewDrive(r".\model")
        self.screwdrive.report.connect(self.NG_Report)
        self.screwdrive.status.connect(self.statusChange)
        self.label_OK.setText('calculating')
        self.All_AIPass = True
        self.All_Report_count = 0
        self.inputimage = copy.deepcopy(cv2.imread(r"D:\Screwdriver_Data\1211_60Boxes\AI\origin\AI_20231211_193650.png"))
        self.Result = copy.deepcopy(self.inputimage)
        self.screwdrive.Result = self.Result
        self.screwdrive.image_AI = cv2.cvtColor(self.Result, cv2.COLOR_BGR2GRAY)
        self.screwdrive.Main(1, self.dbwindow.aoi_start)
        self.screwdrive.image_AOI = cv2.cvtColor(copy.deepcopy(cv2.imread(r"D:\Screwdriver_Data\1211_60Boxes\AI\origin\AI_20231211_193650.png")),
                                                 cv2.COLOR_BGR2GRAY)
        self.screwdrive.AOIimage_ISREADY = True

    def statusChange(self, statusNow):
        # if self.All_AIPass or self.checkBox_saveImage.isChecked():
        #     output_file_name = f'{self.camera.cam.ExposureTime.GetValue()}.png'
        #     output_file_path = fr"D:\ScrewdriverFile\ScrewdriverImage\0922\{output_file_name}"
        #     cv2.imwrite(output_file_path, self.inputimage)
        if statusNow:
            self.Result = cv2.rotate(self.Result, cv2.ROTATE_90_CLOCKWISE)
            self.imageLable_Show(self.label_Image, self.Result)
            self.dbwindow.aoi_end = datetime.now()
            self.dbwindow.write_data()
            print(f'********************結束********************')
    def NG_Report(self, is_OK, confidence, Index):
        try:
            self.All_Report(is_OK, confidence, Index)
            # self.imageLable_Show(self.label_image_Result, self.Result)

            if is_OK == 0:#AI False
                self.All_AIPass = False
        except Exception as e:
            print(e)
    def All_Report(self, is_OK, confidence, Index):
        if not(is_OK in [1, 404]):
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.ng_bits_index = self.All_Report_count + 1
            else:
                self.dbwindow.ng_bits_index = f'{self.dbwindow.ng_bits_index},{self.All_Report_count + 1}'
        self.All_Report_count += 1

        if self.All_Report_count == len(self.MYINI.Class_Name_All):
            print(self.screwdrive.NG_Image_Information.values())
            is_Fuck = len([x for x in self.screwdrive.NG_Image_Information.values() if 'slotted' in x])
            print(f'is_Fuck = {is_Fuck}')
            self.Start24_Count += 1
            if self.dbwindow.ng_bits_index == '':
                self.dbwindow.pass_or_failure = True
                self.DetectOK()
                self.label_OK.setText('OK')
                self.label_OK.setStyleSheet(
                    'background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; font-size: 72px;')
            elif is_Fuck > 8:
                self.dbwindow.ng_bits_index = ''
                self.dbwindow.pass_or_failure = True
                self.DetectNG()
                self.label_OK.setText('不計數')
                self.label_OK.setStyleSheet(
                    'background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px; font-size: 72px;')
            else:
                self.NG_Count += 1
                self.label_OK.setText('NG')
                self.label_OK.setStyleSheet(
                    'background-color: #FF5555; color: white; border-radius: 5px; padding: 10px; font-size: 72px;')
                self.DetectNG()
            print(f'NG : {self.NG_Count} / {self.Start24_Count}')
    def Seach(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', './0712Verify/ROI', 'Image Files(*.png *.jpg *.bmp *.jpeg)')
        self.inputimage_filename = filename
        if filename:
            try:
                self.inputimage = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), -1)
                self.imageLable_Show(self.label_image_Measure_InputImage, self.inputimage)
            except BaseException as e:
                print('openFiles:', e)

    def Main(self):
        self.tableWidget_information_correctrate.clear()
        self.tableWidget_information.clear()
        self.messages_Failure_count = 0
        self.messages_Finish_count = 0
        self.status_engineer = 0

        self.screwDrive_for_test.engineer(rf"{self.comboBox_Validation_set.currentText()}", self.status_engineer, model_fileName=self.comboBox_models.currentText())
        # self.screwdrive.engineer(r"C:\Users\K\Desktop\1201Screwdriver_backup\imageprocess\1208_NG\Milwaukee_AI", 0)
        self.tableWidget_information_correctrate.setHorizontalHeaderLabels(["class_number", "Total", "succese", "failure", "correct_rate"])

    def Test_Measure(self):
        self.status_engineer = 2
        self.screwdrive.engineer(r"C:\Users\user\Desktop\ScrewDriver\trainningset\111", self.status_engineer)#0116
        # threading.Thread(target=self.screwdrive.engineer, args=(r"D:\Screwdriver_Data\KleinTool\aoi\ROI", self.status_engineer)).start()
        # threading.Thread(target=self.screwdrive.engineer, args=(r"D:\Screwdriver_Data\KleinTool\aoi\ROI", self.status_engineer)).start()

        # self.screwdrive.engineer(r"D:\Screwdriver_Data\imageprocess\imageprocess_01161720_BackUp\test", self.status_engineer)
        # self.screwdrive.engineer(r"D:\Screwdriver_Data\ROI_Factory_AOI", self.status_engineer)

    def show_measure(self, measure_dic):
        def Find_string_locate(s):
            # 使用正規表達式找出字串中的英文單字
            matches = re.findall(r'[a-zA-Z]+', s)

            # 如果找到英文單字，則找出該單字後面第二個數字
            print(f'matches = {matches}')
            if matches:
                target_word = matches[0]  # 假設只有一個英文單字
                numbers_after_word = re.findall(rf'{target_word}_\d+', s)
                print(f'numbers_after_word = {numbers_after_word}')
                # 如果找到數字，則輸出第二個數字
                if numbers_after_word:
                    numbers = re.findall(r'\d+', numbers_after_word[0])
                    print(f'numbers = {numbers}')
                    if len(numbers) >= 2:
                        result = int(numbers[1])
                        print(result)
                        return result
                    else:
                        print("找不到足夠的數字")
                else:
                    print("找不到數字")
            else:
                print("找不到英文單字")
        self.tableWidget_information.setRowCount(len(measure_dic))
        self.tableWidget_information.setColumnCount(5)
        row = 0
        index = -1
        for filename, classname_size, diameters, aspect_ratio, vertices in measure_dic:
            item = QTableWidgetItem(filename)
            # 使用正則表達式尋找數字
            numbers = re.findall(r'\d+', filename)
            # 返回符合條件的數字
            nums = [number for number in numbers if int(number) >= 0]
            # 20231213_175019_torxtamperproof_2_20_0.656_6.png
            # ['20231213', '161325', '5', '16', '1', '038', '6']
            # 20231219_225350_torxtamperproof_2_19_0.665_480.0_570.0.png
            # ['20231219', '225350', '2', '19', '0', '665', '480', '0', '570', '0']
            # AOI_20231211_193650.png_roi_15.png
            # ['20231211', '194114', '20']
            # print(nums)
            if len(nums[-2]) == 6:
                num = int(nums[-1])
            else:
                num = int(nums[3])
            numbers = re.findall(r'\d+', classname_size)
            nums = [number for number in numbers if int(number) >= 0]
            if len(nums) > 0:
                size = int(nums[0])
            if not (row == 0) and not (index == num):
                item.setBackground(QColor(29, 230, 181))
            self.tableWidget_information.setItem(row, 0, item)

            item = QTableWidgetItem(str(classname_size))
            # if not (row == 0) and not (num+size == 22):
            #     item.setBackground(QColor(181, 230, 29))
            self.tableWidget_information.setItem(row, 1, item)
            item = QTableWidgetItem(f"{diameters}")
            self.tableWidget_information.setItem(row, 2, item)
            item = QTableWidgetItem(str(aspect_ratio).zfill(6))
            self.tableWidget_information.setItem(row, 3, item)
            item = QTableWidgetItem(str('{:.6f}'.format(round(vertices, 6))).zfill(10))
            self.tableWidget_information.setItem(row, 4, item)
            row += 1
            index = num
    def ShowImage(self, row, column):
        try:
            filenameitem = self.tableWidget_information.item(row, column)
            if column == 0 and filenameitem is not None:
                filename = filenameitem.text()
                if self.status_engineer == 2:
                    self.imageLable_Show(self.label_image_information, self.screwdrive.Measure_dic_Image[filename][0])
                    self.imageLable_Show(self.label_image_histogram, self.screwdrive.Measure_dic_Image[filename][1])
                    self.imageLable_Show(self.label_image_Remedy, self.screwdrive.Measure_dic_Image[filename][2])
                    self.imageLable_Show(self.label_image_extend, self.screwdrive.Measure_dic_Image[filename][3])
                    self.Vertical_Projection_Show(self.screwdrive.Measure_dic_Image[filename][0])
                elif self.status_engineer == 0:
                    self.imageLable_Show(self.label_image_information, self.screwDrive_for_test.ErrorImage[filename])
        except Exception as e:
            self.dev_logger.info(f'ShowImage\n{e}')

    def Histogram_Show(self, image):
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        # 設定直方圖的寬度和高度
        scene = QGraphicsScene(self.graphicsView_Measure)
        self.graphicsView_Measure.setScene(scene)

        bar_width = 2.5
        max_height = max(hist[1:])
        # print(len(hist[1:]))
        # 繪製每個條形
        for i, value in enumerate(hist):
            bar_height = (value / max_height) * 400
            bar = QGraphicsRectItem(i * (bar_width + 1), 400 - bar_height, bar_width, bar_height)
            # 設定條形的顏色
            if i % 5 == 0:
                bar.setBrush(QColor(Qt.red))
            else:
                bar.setBrush(QColor(Qt.blue))
            # 將條形添加到場景中
            scene.addItem(bar)

    def Vertical_Projection_Show(self, image):
        # ret, image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

        vertical_projection = np.sum(image, axis=0)
        # print(vertical_projection)
        # print([x for x, k in enumerate(np.sum(image, axis=0)) if k > 0])

        # 設定直方圖的寬度和高度
        scene = QGraphicsScene(self.graphicsView_Measure)
        self.graphicsView_Measure.setScene(scene)

        bar_width = 2.5
        max_height = max(vertical_projection[1:])/255
        # print(len(hist[1:]))
        # 繪製每個條形
        for i, value in enumerate(vertical_projection):
            bar_height = (value/255 / max_height) * 400
            bar = QGraphicsRectItem(i * (bar_width + 1), 400 - bar_height, bar_width, bar_height)
            # 設定條形的顏色
            if i % 5 == 0:
                bar.setBrush(QColor(Qt.red))
            else:
                bar.setBrush(QColor(Qt.blue))
            # 將條形添加到場景中
            scene.addItem(bar)


    def imageLable_Show(self, image_label, Show_image):
        if len(Show_image.shape) == 3:
            Show_image = cv2.cvtColor(Show_image, cv2.COLOR_BGR2RGB)  # 圖像存儲使用8-8-8 24位RGB格式
        else:
            Show_image = cv2.cvtColor(Show_image, cv2.COLOR_GRAY2RGB)  # 圖像存儲使用8-8-8 24位RGB格式
        rows, cols, channels = Show_image.shape  # 獲取圖片長寬
        QImg = QImage(Show_image.data, cols, rows, cols*channels, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        image_label.setPixmap(pixmap)

    def Measure(self):
        # inputimage = cv2.imread('./VarificationSet0708_model0708batchsize12epoch6/04_Hex/2023-07-08_19-26-09 2.png')
        # 取得目前檔案的絕對路徑
        file_path = os.path.abspath(self.inputimage_filename)
        # 取得檔案所在的資料夾路徑
        folder_path = os.path.dirname(file_path)
        # 取得資料夾名稱
        folder_name = os.path.basename(folder_path)
        image, _, _, _ = Measure(self.inputimage).measure(folder_name)
        self.imageLable_Show(self.label_image_Measure_ROI, image)
        cv2.imwrite('./Measure_result.png', image)

    def receive_message_Finish(self, class_number, Total, succese, failure, correct_rate):
        item = QTableWidgetItem(class_number)
        self.tableWidget_information_correctrate.setItem(self.messages_Finish_count, 0, item)
        item = QTableWidgetItem(Total)
        self.tableWidget_information_correctrate.setItem(self.messages_Finish_count, 1, item)
        item = QTableWidgetItem(succese)
        self.tableWidget_information_correctrate.setItem(self.messages_Finish_count, 2, item)
        item = QTableWidgetItem(failure)
        self.tableWidget_information_correctrate.setItem(self.messages_Finish_count, 3, item)
        item = QTableWidgetItem(correct_rate)
        self.tableWidget_information_correctrate.setItem(self.messages_Finish_count, 4, item)
        self.messages_Finish_count += 1


    def receive_message(self, img_filename, file, class_number, confidence):
        # print(u'正在閱讀新文章內容：%s' % event.dict["artical"])
        item = QTableWidgetItem(img_filename)
        self.tableWidget_information.setItem(self.messages_Failure_count, 0, item)
        item = QTableWidgetItem(file)
        self.tableWidget_information.setItem(self.messages_Failure_count, 1, item)
        item = QTableWidgetItem(class_number)
        self.tableWidget_information.setItem(self.messages_Failure_count, 2, item)
        item = QTableWidgetItem(confidence)
        self.tableWidget_information.setItem(self.messages_Failure_count, 3, item)

        self.messages_Failure_count += 1
        self.tableWidget_information.setRowCount(self.messages_Failure_count+1)

    def AI_Class_Changed(self):
        try:
            self.show_measure(self.screwdrive.Measure_dic[self.comboBox_AI_Class.currentText()])
            self.dev_logger.info(f'AI_Class_Changed Change to  --> {self.comboBox_AI_Class.currentText()}')
        except Exception as e:
            self.dev_logger.info(f'AI_Class_Changed Change to  --> {self.comboBox_AI_Class.currentText()}\n{e}')
    def measure_step(self, class_name):
        self.comboBox_AI_Class.addItem(class_name)


from tensorflow.keras import models
from tensorflow.keras.preprocessing.image import img_to_array

class ScrewDrive_For_Test(QThread):
    trigger = pyqtSignal(str, str, str, str)
    finish = pyqtSignal(str, str, str, str, str)
    output_finish = pyqtSignal(str, str, str, str)
    def __init__(self, identity='apha', myIni=None):
        super().__init__()
        self.Identity = identity
        self.Identity_CodeName = ['alpha', 'beta', 'gamma', 'delta']
        # with tf.device('/cpu:0'):
        self.Myini = myIni
        self.ErrorImage = {}
        self.Input_FilePath = ''
        self.modecode = -1

    def split_digits_in_img(self, img_array):
        x_list = list()
    #    for i in range(digits_in_img):
        x_list.append(img_array)
        return x_list
    def engineer(self, filepath, modecode, model_fileName=None):
        self.modecode = modecode
        self.Input_FilePath = filepath
        self.Test_noimread_Model_FileName = model_fileName
        self.start()
    def Test_noimread(self):
        # print(f'loaded madel : checkpoint\{self.Test_noimread_Model_FileName}')
        Model = models.load_model(fr'D:\ScrewdriverFile\model\0509\13\{self.Test_noimread_Model_FileName}')
        np.set_printoptions(suppress=True, linewidth=150, precision=9, formatter={'float': '{: 0.9f}'.format})
        image_list = list()
        self.Input_FilePath = fr'D:\ScrewdriverFile\ScrewdriverImage\Varification\{self.Input_FilePath}'
        file_list = os.listdir(self.Input_FilePath)
        for k, file in enumerate(file_list):
            img_filenames = os.listdir(fr'{self.Input_FilePath}/{file}')
            for img_filename in img_filenames:
                InputImage = cv2.imread(fr'{self.Input_FilePath}/{file}/{img_filename}', cv2.IMREAD_GRAYSCALE)
                image_list.append(image_k_file_img(k, file, img_filename, InputImage))
        start = time.time()
        class_list_correct_rate = list()
        succese = 0
        failure = 0
        class_end = False
        class_start = -1
        imgs_array = [
            np.expand_dims(img_to_array(cv2.resize(img.Image, (112, 112), interpolation=cv2.INTER_CUBIC)), axis=0) for
            img in image_list]
        x = np.concatenate([x for x in imgs_array])
        if len(file_list) == 3:
            print('small')
            result_class = Model.predict(x, verbose=0)
        else:
            print('normal')
            result_class = Model.predict(x, verbose=0)
        print(f'result_class = {result_class}')
        result_Max_Index = [np.argmax(r_c, axis=0) for r_c in result_class]
        print(f'result_Max_Index = {result_Max_Index}')

        class_names_AI = [file_list[int(Index)] for Index in result_Max_Index]
        confidences = [str(result_class[i][Index]) for i, Index in enumerate(result_Max_Index)]
        index_class = [index.Image_Index for index in image_list]
        for i, image in enumerate(image_list):
            if image.Image_Index is not class_start and class_end:
                class_end = False
                print('')
                correct_rate = round(succese / (succese + failure), 3)
                class_list_correct_rate.append(correct_rate)
                self.send_message_Finish(
                    [image_list[i-1].file, str(succese + failure), str(succese), str(failure), str(correct_rate)])
                print(
                    f'********************************************** 正確率 = {correct_rate} **********************************************')
            if image.Image_Index is not class_start:
                class_start = image.Image_Index
                class_end = True
                succese = 0
                failure = 0
                print(
                    f' ********************************************** file_list = {image.file} **********************************************')
            if class_names_AI[i] == file_list[index_class[i]]:
                succese += 1
            else:
                self.send_message([image.img_filename, image.file, class_names_AI[i], confidences[i]])
                self.ErrorImage[image.img_filename] = image.Image
                failure += 1
        print('')
        correct_rate = round(succese / (succese + failure), 3)
        class_list_correct_rate.append(correct_rate)
        self.send_message_Finish([image_list[i - 1].file, str(succese + failure), str(succese), str(failure), str(correct_rate)])

        print(f'********************************************** 正確率 = {correct_rate} **********************************************')
        for i in range(len(class_list_correct_rate)):
            print(f'{file_list[i]} 的正確率 = {class_list_correct_rate[i]}')
        end = time.time()
        print(f' ------------------------------------ 耗時 --> {(end - start)} ------------------------------------')
    def send_message(self, message):
        # 事件物件，寫了新文章
        self.trigger.emit(message[0], message[1], message[2], message[3])

    def send_message_Finish(self, message):
        # 事件物件，寫了新文章
        self.finish.emit(message[0], message[1], message[2], message[3], message[4])

    def run(self):
        if self.modecode == 0:
            self.Test_noimread()
class image_k_file_img:
    def __init__(self, k, file, img_filename,  img):
        self.Image_Index = k
        self.file = file
        self.img_filename = img_filename
        self.Image = img
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 固定的，PyQt5程式都需要QApplication對象。sys.argv是命令列參數清單，確保程式可以按兩下運行
    MyWindow = MainWindow()  # 初始化
    MyWindow.show()  # 將視窗控制項顯示在螢幕上
    sys.exit(app.exec_())  # 程式運行，sys.exit方法確保程式完整退出
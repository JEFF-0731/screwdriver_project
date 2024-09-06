import configparser
import copy
import glob
import logging
import math
import re
import threading
from datetime import datetime
import pandas as pd

import numpy as np
import os
import sys
import csv
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import time
# import imutils
from concurrent.futures import ThreadPoolExecutor, as_completed

class ScrewDrive(QThread):
    report = pyqtSignal(int, str, int, str, str)
    trigger = pyqtSignal(str, str, str, str)
    finish = pyqtSignal(str, str, str, str, str)
    output_finish = pyqtSignal(str, str, str, str)
    status = pyqtSignal(bool)
    Measure_Step = pyqtSignal(str)

    def __init__(self, model_filepath=None, dev_logger=None, identity='apha', myIni=None):
        super().__init__()

        self.Identity = identity
        self.Identity_CodeName = ['alpha', 'beta', 'gamma', 'delta']
        print(f'Identity = {self.Identity}')
        # with tf.device('/cpu:0'):
        self.Myini = myIni

        if dev_logger == None:
            self.iniLogging()
            self.dev_logger.info('Program Start')
        else:
            self.dev_logger = dev_logger

        if model_filepath == None:
            print('Only Measure !!')
        else:
            self.models = list()

            self.models.append(YOLO(f'{model_filepath}/{self.Myini.recipe_model}.pt'))
            print(f'loaded madel : {model_filepath}/{self.Myini.recipe_model}.pt')

            # self.models.append(models.load_model(f'{model_filepath}/{self.Myini.recipe_model}.h5'))
            # print(f'loaded madel : {model_filepath}/{self.Myini.recipe_model}.h5')

            # np.set_printoptions(suppress=True, linewidth=150, precision=9, formatter={'float': '{: 0.9f}'.format})
            threading.Thread(target=self.First, args=()).start()


        self.input_image_list = list()
        self.ErrorImage = {}
        self.image_AI = []
        self.image_AOI = []
        self.Result = []
        self.Input_FilePath = ''
        self.modecode = -1
        self.AOIimage_ISREADY = False
        self.lock = threading.Lock()
        self.average_gray_values = list()
        self.Predict_Result = list()  # Output of self.Predict_Image(img, i), Input to AOI and Report
        # self.read_ini()

        self.Measure_dic = {}
        self.Measure_dic_Image = {}
        self.NG_Image_Information = {}
        # print(self.Measuresize('pentalope', cv2.imread(r".\1202AOI_exp36000\ROI\11_Pentalope\2023_12_02_13_41_34_roi_28.png", cv2.IMREAD_COLOR), 28))
        img_filenames = os.listdir(f'./imageprocess/{self.Myini.recipe}/AI')
        self.Filenames_for_Record = list()
        for img_filename in img_filenames:
            self.Filenames_for_Record.append(img_filename)
    def First(self):
        image = cv2.imread(
            r".\First\First.png",
            cv2.IMREAD_GRAYSCALE)
        self.models[0](image)

    def iniLogging(self):
        logging_FileName = time.strftime('%Y%m%d')

        self.dev_logger: logging.Logger = logging.getLogger(name='dev')
        self.dev_logger.setLevel(logging.DEBUG)

        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        self.dev_logger.addHandler(handler)
        os.makedirs(rf'./Logging/', exist_ok=True)

        file_handler: logging.FileHandler = logging.FileHandler(rf'.\Logging\{logging_FileName}_dev.log', mode='a')
        file_handler.setFormatter(formatter)
        self.dev_logger.addHandler(file_handler)
    def Main(self,modecode, time):
        print(f'Main modecode = {modecode}')
        self.Time_for_Record = time.strftime('%Y%m%d_%H%M%S')
        self.modecode = modecode
        self.start()

    def engineer(self, filepath, modecode):
        self.modecode = modecode
        self.Input_FilePath = filepath
        self.start()

    def run(self):
        if self.modecode == 0:
            self.Test_noimread()
        elif self.modecode == 2:
            os.makedirs(f'./Measure_CSV', exist_ok=True)
            os.makedirs(f'./Measure', exist_ok=True)
            self.Test_Measure()
        elif self.modecode == 1:
            self.To_Run()

    def To_Run(self):
        # print(f'self.Pre_ROI_Dic = {self.Myini.Pre_ROI_Dic}')
        print(f'self.Identity = {self.Identity}')
        # print(f'self.ROI_List = {self.Myini.ROI_List}')
        self.image_AI = self.image_AI[self.Myini.Pre_ROI_Dic[self.Identity][1]:self.Myini.Pre_ROI_Dic[self.Identity][1] + self.Myini.Pre_ROI_Dic[self.Identity][3], self.Myini.Pre_ROI_Dic[self.Identity][0]:self.Myini.Pre_ROI_Dic[self.Identity][0] + self.Myini.Pre_ROI_Dic[self.Identity][2]]
        self.Result = self.Result[self.Myini.Pre_ROI_Dic[self.Identity][1]:self.Myini.Pre_ROI_Dic[self.Identity][1] + self.Myini.Pre_ROI_Dic[self.Identity][3], self.Myini.Pre_ROI_Dic[self.Identity][0]:self.Myini.Pre_ROI_Dic[self.Identity][0] + self.Myini.Pre_ROI_Dic[self.Identity][2]]
        # print(f'self.Result.shape = {self.Result.shape}')

        self.AOIimage_ISREADY = False
        starttime = time.time()

        Images_AI = self.ROI(self.image_AI)
        class_names_AI, confidences, Index = self.Predict_Images_YOLOv8(Images_AI, 0)
        # print(f'class_names_AI = {class_names_AI}')

        endtime = time.time()
        print(f'!!推論時間 : {endtime - starttime}')

        # start = time.time()
        # end_ROI = time.time()
        # self.parallel_processing_AllImage(self.input_image_list, 0, self.lock)
        # threads = list()
        # for i, sl in enumerate(split_list(self.input_image_list, wanted_parts=len(self.models))):
        try:
            self.parallel_processing_AllImage(class_names_AI, Index, confidences, 0, self.lock, Images_AI)
        except Exception as e:
            self.dev_logger.error(f'parallel_processing_AllImage\n{e}')

        self.status.emit(True)

        def split_list(alist, wanted_parts=1):
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

    def DrawResult(self, ROI_List_index, b, g, r):
        # print(f'{self.Identity} DrawResult')
        self.lock.acquire()
        cv2.rectangle(self.Result,
                      (self.Myini.ROI_List[ROI_List_index].X_start, self.Myini.ROI_List[ROI_List_index].Y_start),
                      (self.Myini.ROI_List[ROI_List_index].X_stop, self.Myini.ROI_List[ROI_List_index].Y_stop),
                      (b, g, r), 3)
        self.lock.release()
    def parallel_processing_AllImage(self, class_names_AI, Index, confidences, models_index, lock, images_ai): #同時
        while self.AOIimage_ISREADY == False:
            time.sleep(0.01)
            print('.')
        self.image_AOI = self.image_AOI[self.Myini.Pre_ROI_Dic[self.Identity][1]:self.Myini.Pre_ROI_Dic[self.Identity][1] + self.Myini.Pre_ROI_Dic[self.Identity][3], self.Myini.Pre_ROI_Dic[self.Identity][0]:self.Myini.Pre_ROI_Dic[self.Identity][0] + self.Myini.Pre_ROI_Dic[self.Identity][2]]
        # cv2.imwrite(f'./imageprocess/{self.Identity}.png', self.image_AOI)

        AOI_Time = time.time()
        imgs = self.ROI(self.image_AOI)
        for img in imgs:
            is_NG = False
            is_NotValid = False
            i = img.Image_Index

            # diameter = '999'
            # aspect_ratio = '999'
            # numberofvertices = '999'
            # image_measure = img.Image

            try:
                class_name, image_measure, diameter, aspect_ratio, numberofvertices = self.Measuresize(class_names_AI[Index.index(i)], img.Image, i)
            except Exception as e:
                diameter = 0
                numberofvertices = 0
                class_name = f'{class_names_AI[Index.index(i)]}_0'
                self.dev_logger.error(f'Measuresize\n{e}')
            # class_name = class_names_AI[Index.index(i)]

            print(f'{self.Myini.Class_Name_All[i]} --> {class_name} index = {Index.index(i)}')
            self.NG_Image_Information[self.Myini.Class_Name_All[i]] = class_name
            if class_name == self.Myini.Class_Name_All[i]:
                self.report.emit(1, confidences[Index.index(i)], i, diameter, numberofvertices)
                self.DrawResult(i, 0, 255, 0)
                # print(f'成功 第{i}張 {self.Myini.Class_Name_All[i]}')
            elif 'NotValid' in class_name:
                is_NotValid = True
                cv2.imwrite(f'./imageprocess/{self.Myini.recipe}/NotValid/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',image_measure)
                cv2.imwrite(f'./imageprocess/{self.Myini.recipe}/NotValid_Origin/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',img.Image)
                self.report.emit(404, confidences[Index.index(i)], i, diameter, numberofvertices)
                self.send_output_message_Finish(
                    [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('NotValid'), str(class_name)])
                self.DrawResult(i, 0, 0, 255)
            # elif class_name in ['vacancy', 'opposite']:
            #     print(f'{class_name}進來了')
            #     self.send_output_message_Finish(
            #         [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('無放插件'), 'Vacancy'])
            #     self.report.emit(10, 'Vacancy', i, diameter, numberofvertices)
            #     self.DrawResult(i, 255, 0, 0)
            elif class_name in ['vacancy']:
                print(f'{class_name}進來了')
                self.send_output_message_Finish(
                    [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('無放插件'), 'Vacancy'])
                self.report.emit(10, 'Vacancy', i, diameter, numberofvertices)
                self.DrawResult(i, 255, 0, 0)
            elif class_name in ['opposite']:
                print(f'{class_name}進來了')
                self.send_output_message_Finish(
                    [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('倒放插件'), 'Opposite'])
                self.report.emit(10, 'Opposite', i, diameter, numberofvertices)
                self.DrawResult(i, 255, 0, 0)
            elif class_name.split('_')[0] == self.Myini.Class_Name_All[i].split('_')[0]:
                if class_name.split('_')[0] == 'phillips':
                    is_NG = True
                    self.report.emit(0, confidences[Index.index(i)], i, diameter, numberofvertices)
                    self.send_output_message_Finish(
                        [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('AI失敗'), str(class_name)])
                    self.DrawResult(i, 0, 0, 255)
                    # print(f'AI失敗 第{i}張 {self.Myini.Class_Name_All[i]} 預測結果 : {class_name}')
                else:
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',
                        image_measure)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI_Origin/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',
                        img.Image)
                    self.report.emit(-1, confidences[Index.index(i)], i, diameter, numberofvertices)
                    self.send_output_message_Finish(
                        [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('AOI失敗'), str(class_name)])
                    self.DrawResult(i, 0, 0, 255)
                    # print(f'AOI失敗 第{i}張 {self.Myini.Class_Name_All[i]} 預測結果 : {class_name}')
            else:
                is_NG = True
                self.report.emit(0, confidences[Index.index(i)], i, diameter, numberofvertices)
                self.send_output_message_Finish(
                    [f'第{i}張', str(self.Myini.Class_Name_All[i]), str('AI失敗'), str(class_name)])
                self.DrawResult(i, 0, 0, 255)
                # print(f'AI失敗 第{i}張 {self.Myini.Class_Name_All[i]} 預測結果 : {class_name}')
            if is_NG or is_NotValid:
                NG_Record = self.Myini.Class_Name_All[i].split('_')[0]
                if NG_Record == 'phillips':
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}.png',
                        image_measure)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI_Origin/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}.png',
                        img.Image)

                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AI/{self.Filenames_for_Record[self.Myini.Class_Name_AI.index(self.Myini.Class_Name_All[i])]}/{self.Time_for_Record}_{class_name}_{i}_{confidences[Index.index(i)]}.png',
                        images_ai[i].Image)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI_ForAIPredict/{self.Filenames_for_Record[self.Myini.Class_Name_AI.index(self.Myini.Class_Name_All[i])]}/{self.Time_for_Record}_{class_name}_{i}_{confidences[Index.index(i)]}.png',
                        img.Image)
                else:
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',
                        image_measure)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI_Origin/{self.Time_for_Record}_{class_name}_{i}_{diameter}_{numberofvertices}_{aspect_ratio}.png',
                        img.Image)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AI/{self.Filenames_for_Record[self.Myini.Class_Name_AI.index(NG_Record)]}/{self.Time_for_Record}_{class_name}_{i}_{confidences[Index.index(i)]}.png',
                        images_ai[i].Image)
                    cv2.imwrite(
                        f'./imageprocess/{self.Myini.recipe}/AOI_ForAIPredict/{self.Filenames_for_Record[self.Myini.Class_Name_AI.index(NG_Record)]}/{self.Time_for_Record}_{class_name}_{i}_{confidences[Index.index(i)]}.png',
                        img.Image)
        print(f'!!AOI量測 : {time.time() - AOI_Time}')

    def Measuresize(self, classname, image, count):
        # print(classname)
        # print(self.Myini.Class_Name_All[count])
        if self.Myini.NotValid_dic[classname][0] == 0:
            return classname, image, str(0), 0, str(0)
        try:
            image_measure, diameter, aspect_ratio, numberofvertices = Measure(image).measure(classname,recipe=self.Myini.recipe)#82207
        except Exception as e:
            diameter = 0
            image_measure = image
            aspect_ratio = 29
            numberofvertices = 0
            print(f'measure\n{e}')
            self.dev_logger.error(f'measure\n{e}')

        # 不一樣才進去
        # AI推論為非插件錯放
        # 判錯放對
        if not (classname in self.Myini.Class_Name_All[count]):
            # ini檔角數量不是0
            # 誤判種類算出來的角數量不等於這個位置的種類算出來的角數量
            # 才進去
            if not (self.Myini.NotValid_NumberOfVertices_dic[classname] == 0) and not (numberofvertices == self.Myini.NotValid_NumberOfVertices_dic[classname]):
                if classname == 'torx' and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['pentalope']:
                    classname = 'pentalope'
                elif classname == 'pentalope' and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['torx']:
                    if diameter < self.Myini.MeasureSize_dic['pentalope'][0]:
                        pass
                    if diameter > self.Myini.MeasureSize_dic['pentalope'][0]:
                        classname = 'torx'
                else:
                    return f'{classname}_NotValidNOV', image_measure, str(diameter), aspect_ratio, str(
                        numberofvertices)
            elif classname == 'triwing' and numberofvertices in [5, 6]:
                if diameter < self.Myini.MeasureSize_dic['pentalope'][0]:
                    classname = 'pentalope'

            elif classname == 'slotted' and aspect_ratio > 0.4:
                if diameter > self.Myini.MeasureSize_dic['square'][0] and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['square']:
                    print('square in up')
                    classname = 'square'

                elif diameter > self.Myini.MeasureSize_dic['triangle'][0] and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['triangle']:
                    print('triangle in up')
                    classname = 'triangle'

                elif self.Myini.MeasureSize_dic['triwing'][1] > diameter > self.Myini.MeasureSize_dic['triwing'][0] and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['triwing']:
                    print('triwing in up')
                    classname = 'triwing'

                elif diameter < self.Myini.MeasureSize_dic['hex'][0]:
                    print('hex in up')
                    classname = 'hex'

                elif diameter > self.Myini.MeasureSize_dic['torx'][0] and numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['torx']:
                    print('torx in up')
                    classname = 'torx'

            for k, d in enumerate(self.Myini.NotValid_dic[classname]):
                if diameter > self.Myini.NotValid_dic[classname][-1]:
                    return f'{classname}_NotValid', image_measure, str(diameter), aspect_ratio, str(numberofvertices)
                if diameter <= d:
                    if k % 2 == 1:
                        break
                    else:
                        return f'{classname}_NotValid', image_measure, str(diameter), aspect_ratio, str(numberofvertices)
        # 判錯放錯
        elif classname == 'torx':
            if diameter > self.Myini.MeasureSize_dic['torx'][0]:
                if numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['pentalope']:
                    classname = 'pentalope'

        elif classname == 'pentalope':
            if diameter > self.Myini.MeasureSize_dic['pentalope'][0]:
                if numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['torx']:
                    classname = 'torx'

        if classname == 'slotted':
            if aspect_ratio > 0.4 and ('hex' in self.Myini.Class_Name_All[count] or 'slotted' in self.Myini.Class_Name_All[count]):
                print('hex in down')
                classname = 'hex'
            elif numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['square'] and aspect_ratio > 0.4:
                print('square in down')
                classname = 'square'
            elif numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['triangle'] and aspect_ratio > 0.4:
                print('triangle in down')
                classname = 'triangle'
            elif numberofvertices == self.Myini.NotValid_NumberOfVertices_dic['torx'] and aspect_ratio > 0.4:
                print('torx in down')
                classname = 'torx'

        if classname == 'opposite':
            return f'Bottom', image_measure, str(diameter), aspect_ratio, str(numberofvertices)

        if classname in ['torxtamperproof'] and self.Myini.recipe == 'Milwaukee':
            size = 0
            for i in self.Myini.MeasureSize_Approx_ArcLength_dic[classname]:
                if (aspect_ratio - i) > 0:
                    size += 1

            if not (self.Myini.Class_Name_All[count] == f'{classname}_{size + 1}'):
                size_diameter = 0
                for i in self.Myini.MeasureSize_dic[classname]:
                    if (diameter - i) > 0:
                        size_diameter += 1
                size_Approx_Area = 0
                for i in self.Myini.MeasureSize_Approx_Area_dic[classname]:
                    if (numberofvertices - i) > 0:
                        size_Approx_Area += 1

                if self.Myini.Class_Name_All[count] in [f'{classname}_{size_Approx_Area + 1}',
                                                        f'{classname}_{size_diameter + 1}']:
                    return self.Myini.Class_Name_All[count], image_measure, str(diameter), aspect_ratio, str(
                        numberofvertices)
                else:
                    return f'{classname}_{size + 1}', image_measure, str(diameter), aspect_ratio, str(
                        numberofvertices)

            else:
                return f'{classname}_{size + 1}', image_measure, str(diameter), aspect_ratio, str(numberofvertices)
        else:
            if self.Myini.MeasureSize_dic[classname][0] == 0:
                return classname, image_measure, str(diameter), aspect_ratio, str(numberofvertices)
            size = 0
            for i in self.Myini.MeasureSize_dic[classname]:
                if (diameter - i) > 0:
                    size += 1
            return f'{classname}_{size + 1}', image_measure, str(diameter), aspect_ratio, str(numberofvertices)

    def ROI(self, Image):
        try:
            result = [Image_and_Index(Image[roi_data.Y_start:roi_data.Y_stop, roi_data.X_start:roi_data.X_stop], i) for i, roi_data in enumerate(self.Myini.ROI_List)]
            # result = list()
            # for i, roi_data in enumerate(self.Myini.ROI_List):

            #     result.append(Image_and_Index(Image[roi_data.Y_start:roi_data.Y_stop, roi_data.X_start:roi_data.X_stop], i))
        except Exception as e:
            self.dev_logger.error(f'ROI\n{e}')
        return result


    def FindMaxContours(self, contours):
        area = []
        for contour in contours:
            area.append(cv2.contourArea(contour))
        max_idx = np.argmax(np.array(area))
        return max_idx

    def Test_Measure(self):
        start = time.time()
        file_list = os.listdir(self.Input_FilePath)

        for k, file in enumerate(file_list):
            print(f' ********************************************** file_list = {file[3:].lower()} **********************************************')
            img_filenames = os.listdir(f'{self.Input_FilePath}/{file}')
            diameter_array = list()
            aspect_ratio_array = list()
            area_array = list()
            classname_size_array = list()
            for img_filename in img_filenames:
                def size_judge(d, a_approx, a, img_filename):
                    def Get_Locate(f):
                        nums = [number for number in re.findall(r'\d+', f) if int(number) >= 0]
                        if len(nums[-2]) == 6:
                            num = int(nums[-1])
                        else:
                            num = int(nums[-4])
                        return num
                    if self.Myini.MeasureSize_dic[file[3:].lower()][0] == 0:
                        cs = file[3:].lower()
                    elif self.Myini.MeasureSize_Approx_ArcLength_dic[file[3:].lower()] == 0:
                        size = 0
                        for i in self.Myini.MeasureSize_dic[file[3:].lower()]:
                            if (d - i) > 0:
                                size += 1
                        cs = f'{file[3:].lower()}_{size + 1}'
                    else:
                        locate = Get_Locate(img_filename)
                        size = 0
                        for i in self.Myini.MeasureSize_Approx_Area_dic[file[3:].lower()]:
                            if (a_approx - i) > 0:
                                size += 1

                        if a_approx < (self.Myini.MeasureSize_Approx_Area_dic[file[3:].lower()][size-1] if size > 0 else 0) * 1.02 or a_approx > (self.Myini.MeasureSize_Approx_Area_dic[file[3:].lower()][size] if size < len(self.Myini.MeasureSize_Approx_Area_dic[file[3:].lower()]) else 100000) * 0.98 or not (size + 1 + locate == 22):
                            size_diameter = 0
                            for i in self.Myini.MeasureSize_dic[file[3:].lower()]:
                                if (d - i) > 0:
                                    size_diameter += 1

                            size_Area = 0
                            for i in self.Myini.MeasureSize_Approx_ArcLength_dic[file[3:].lower()]:
                                if (a - i) > 0:
                                    size_Area += 1
                            cs = f'{file[3:].lower()}_{size + 1}_{size_diameter + 1}_{size_Area + 1}'
                        else:
                            cs = f'{file[3:].lower()}_{size + 1}'
                    return cs

                print(img_filename)
                # 讀取
                path = f'{self.Input_FilePath}/{file}/{img_filename}'
                InputImage = cv2.imread(f'{self.Input_FilePath}/{file}/{img_filename}')
                measure_object = Measure(InputImage)
                # image, diameter, aspect_ratio, vertices = measure_object.measure_for_KleinTool(file[3:].lower())
                image, diameter, aspect_ratio, vertices = measure_object.measure(file[3:].lower())

                classname_size = size_judge(diameter, aspect_ratio, vertices, img_filename)

                self.Measure_dic_Image[img_filename] = [image, measure_object.Histogram, measure_object.Remedy]
                os.makedirs(f'./Measure/{file}', exist_ok=True)
                cv2.imwrite(f'./Measure/{file}/{img_filename}', image)
                diameter_array.append(diameter)
                aspect_ratio_array.append(aspect_ratio)
                area_array.append(vertices)
                classname_size_array.append(classname_size)
            def myFunc(e):
                return e[2]
            result = list(zip(img_filenames, classname_size_array, diameter_array, aspect_ratio_array, area_array))
            result.sort(reverse=False, key=myFunc)
            self.Measure_dic[file[3:].lower()] = result
            self.write_csv(file, result)
            self.Measure_Step.emit(file[3:].lower())

        file_list = os.listdir('./Measure_CSV/csv')
        # 初始化一個空的DataFrame
        merged_df = pd.DataFrame()
        # 迴圈讀取每個CSV檔案，並將其合併到merged_df中
        for file in file_list:
            df = pd.read_csv(fr'./Measure_CSV/csv/{file}')
            merged_df = pd.concat([merged_df, df], axis=1)

        # 將合併後的DataFrame寫入新的CSV檔案
        merged_df.to_csv(r'./Measure_CSV/Combined_Result.csv', index=False)


        end = time.time()
        print(f' ------------------------------------ 耗時 --> {(end - start)} ------------------------------------')
    def write_csv(self, file_path, data):
        with open(rf'.\Measure_CSV\csv\{file_path}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f'{file_path}', 'classname_size', 'diameters', 'aspect ratio', 'Approximate contour angle number'])  # 寫入標題行
            # 寫入每個 epoch 的 mean_loss 和 acc
            for filename, classname_size, diameters, a, area in data:
                writer.writerow([filename, diameters, a, area])

    def send_message(self, message):
        # 事件物件，寫了新文章
        self.trigger.emit(message[0], message[1], message[2], message[3])

    def send_message_Finish(self, message):
        # 事件物件，寫了新文章
        self.finish.emit(message[0], message[1], message[2], message[3], message[4])

    def send_output_message_Finish(self, message):
        # 事件物件，寫了新文章
        self.output_finish.emit(message[0], message[1], message[2], message[3])

    def split_digits_in_img(self, img_array):
        x_list = list()
    #    for i in range(digits_in_img):
        x_list.append(img_array)
        return x_list

    def Predict_Images_YOLOv8(self, images, models_Index):
        try:
            results = self.models[models_Index]([img.Image for img in images])
            result_Max_Index = [result.probs.top1 for result in results]
            class_numbers = [self.Myini.Class_Name_AI[int(Index)] for Index in result_Max_Index]

            confidences = ['29' for i, Index in enumerate(result_Max_Index)]
        except Exception as e:
            self.dev_logger.error(f'Predict_Images\n{e}')
        return class_numbers, confidences, [index.Image_Index for index in images]


    def DrawImage_VarificationCode(image, varification_code):
        Image_resize_ToSee = cv2.resize(image, (500, 500), interpolation=cv2.INTER_CUBIC)
        cv2.rectangle(Image_resize_ToSee, (100, 100), (130, 50), (255), -1)
        text_varification_code = '{0}'.format(varification_code)
        cv2.putText(Image_resize_ToSee, text_varification_code, (100, 100), cv2.FONT_HERSHEY_PLAIN, 5, (0), 1, cv2.LINE_AA)
        return Image_resize_ToSee

class Measure:
    def __init__(self, inputimage, dev_logger=None):
        # if dev_logger == None:
        #     def iniLogging():
        #         logging_FileName = time.strftime('%Y%m%d')
        #
        #         self.dev_logger: logging.Logger = logging.getLogger(name='dev')
        #         self.dev_logger.setLevel(logging.DEBUG)
        #
        #         handler: logging.StreamHandler = logging.StreamHandler()
        #         formatter: logging.Formatter = logging.Formatter(
        #             '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
        #         handler.setFormatter(formatter)
        #         self.dev_logger.addHandler(handler)
        #
        #         file_handler: logging.FileHandler = logging.FileHandler(
        #             rf'.\Logging\Measure\{logging_FileName}_dev.log', mode='a')
        #         file_handler.setFormatter(formatter)
        #         self.dev_logger.addHandler(file_handler)
        #     iniLogging()
        # else:
        #     self.dev_logger = dev_logger

        self.InputImage = copy.deepcopy(inputimage)
        self.Recipe_NoMask = ['KleinTool']
        self.Histogram = []
        self.Remedy = []
    def measure(self, classnumber, recipe='Milwaukee'):
        print(f'measure_{classnumber}')
        if recipe == 'Milwaukee':
            aspect_ratios = 29
            if len(self.InputImage.shape) == 3:
                inputimage = cv2.cvtColor(self.InputImage, cv2.COLOR_BGR2GRAY)  # 圖像存儲使用8-8-8 24位RGB格式
            else:
                inputimage = copy.deepcopy(self.InputImage)
                self.InputImage = cv2.cvtColor(self.InputImage, cv2.COLOR_GRAY2BGR)
            # GaussianBlur = cv2.GaussianBlur(inputimage, (31, 31), 0)

            maskimage = self.GetMask(inputimage)
            if maskimage is []:
                return self.InputImage, 0, 0, 0

            if classnumber == 'spanner' or classnumber == '03_Spanner':
                _, Threshold_Image = cv2.threshold(inputimage, 60, 255, cv2.THRESH_BINARY)
                count_zero_pixels = (Threshold_Image == 255).sum()
                # print(count_zero_pixels)
                return Threshold_Image, count_zero_pixels, 0, 0
            elif classnumber == 'square':
                ret, Threshold_Image = cv2.threshold(inputimage, 130, 255, cv2.THRESH_BINARY)
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
            elif classnumber == 'hextamperproof':
                ret, Threshold_Image = cv2.threshold(inputimage, 120, 255, cv2.THRESH_BINARY)
                cv2.imwrite(f'./Measure/ht_1_Threshold_Image.png', Threshold_Image)
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
                cv2.imwrite(f'./Measure/ht_2_maskimage.png', maskimage)
                cv2.imwrite(f'./Measure/ht_3_Threshold_Image_And.png', Threshold_Image)
            elif classnumber == 'triwing':
                ret, Threshold_Image = cv2.threshold(inputimage, 100, 255, cv2.THRESH_BINARY)  # 120
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
            elif classnumber == 'torxtamperproof':
                ret, Threshold_Image = cv2.threshold(inputimage, 120, 255, cv2.THRESH_BINARY)  # 120
                cv2.imwrite(f'./Measure/tt_1_Threshold_Image.png', Threshold_Image)
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
                cv2.imwrite(f'./Measure/tt_2_maskimage.png', maskimage)
                cv2.imwrite(f'./Measure/tt_3_Threshold_Image_And.png', Threshold_Image)
            elif classnumber == 'slotted':
                ret, Threshold_Image = cv2.threshold(inputimage, 120, 255, cv2.THRESH_BINARY)  # 150
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
            else:
                ret, Threshold_Image = cv2.threshold(inputimage, 136, 255, cv2.THRESH_BINARY)#145
                cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)

            contours, _ = cv2.findContours(Threshold_Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if classnumber == 'torxtamperproof':
                max_idx = self.FindMaxContours_For_torxtamperproof(contours)
            else:
                max_idx = self.FindMaxContours_For_Other(contours)
            if max_idx > -1:
                torxtamperproof_area = 0
                torxtamperproof_approx_arcLength = 0
                torxtamperproof_approx_area = 0
                square_area = 0
                vertices = 0
                (x, y), radius = cv2.minEnclosingCircle(contours[max_idx])
                center = (int(x), int(y))

                radius_int = int(radius)

                if classnumber in ['hextamperproof']:
                    count = 1
                    mask = np.zeros(Threshold_Image.shape, dtype='uint8')
                    cv2.circle(mask, center, radius_int, (255, 255, 255), -1)

                    new_image = cv2.bitwise_and(inputimage, mask)
                    cv2.imwrite(f'./Measure/ht_4_new_image.png', new_image)
                    mean_value = cv2.mean(new_image[center[1] - radius_int:center[1] + radius_int,center[0] - radius_int:center[0] + radius_int])  # 計算套頭形狀部分的亮度平均值
                    threshold_value = int(mean_value[0] * 1.2)  # 計算inputimage的閾值

                    ret, Threshold_Image_mean_value = cv2.threshold(inputimage, threshold_value, 255,cv2.THRESH_BINARY)  # 二值化
                    self.Histogram = cv2.bitwise_not(Threshold_Image_mean_value)
                    contours_hextamperproof, hierarchy = cv2.findContours(cv2.bitwise_not(Threshold_Image_mean_value),
                                                                          cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

                    i = 0
                    hierach_id = 0
                    inner_class = []
                    while not (hierarchy[0][i][2] == -1) and hierarchy[0][i][1] == -1 and i < len(
                            contours_hextamperproof) and not (hierarchy[0][i][3] == -1):
                        hierach_id = i
                        i += 1
                    # print(hierach_id, hierarchy[0][hierach_id])
                    while not (hierarchy[0][hierach_id][0] == -1):
                        inner_class.append(contours_hextamperproof[hierach_id])
                        hierach_id = hierarchy[0][hierach_id][0]
                        # print(hierach_id, hierarchy[0][hierach_id])


                    Max_contour_index_hextamperproof = self.FindMaxContours_For_hextamperproof(inner_class)  # 找最大輪廓

                    (x, y), radius = cv2.minEnclosingCircle(inner_class[Max_contour_index_hextamperproof])  # 找最大輪廓最小外接園的直徑和圓心
                    center = (int(x), int(y))
                    radius_int = int(radius)
                    cv2.circle(self.InputImage, center, radius_int, (0, 242, 255), 1)

                elif classnumber in ['torxtamperproof']:
                    mask = np.zeros(Threshold_Image.shape, dtype='uint8')
                    # self.Histogram = cv2.bitwise_and(inputimage, maskimage, inputimage)
                    cv2.circle(mask, center, radius_int, (255, 255, 255), -1)
                    new_image = cv2.bitwise_and(inputimage, mask)
                    cv2.imwrite(f'./Measure/tt_4_new_image.png', new_image)
                    mean_value = cv2.mean(new_image[center[1]-radius_int:center[1]+radius_int, center[0]-radius_int:center[0]+radius_int])
                    threshold_value = int(mean_value[0]*1.36)#1.36
                    ret, Threshold_Image_mean_value = cv2.threshold(inputimage, threshold_value, 255, cv2.THRESH_BINARY)
                    contours_torxtamperproof, _ = cv2.findContours(cv2.bitwise_and(Threshold_Image_mean_value, maskimage), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                    testContoursImage = self.InputImage.copy()
                    cv2.drawContours(testContoursImage, contours_torxtamperproof, -1, (255, 0, 0), 1)
                    cv2.imwrite(f'./Measure/tt_5_testContoursImage.png', testContoursImage)

                    Max_contour_index_torxtamperproof = self.FindMaxContours_For_torxtamperproof(contours_torxtamperproof)
                    cv2.drawContours(self.InputImage, contours_torxtamperproof, Max_contour_index_torxtamperproof, (99, 242, 50), 1)

                    testContoursImage2 = self.InputImage.copy()
                    cv2.drawContours(testContoursImage2, contours_torxtamperproof, Max_contour_index_torxtamperproof, (255, 0, 0), 1)
                    cv2.imwrite(f'./Measure/tt_6_testContoursImage.png', testContoursImage2)

                    (x, y), radius = cv2.minEnclosingCircle(contours_torxtamperproof[Max_contour_index_torxtamperproof])

                    epsilon = 0.045 * cv2.arcLength(contours_torxtamperproof[Max_contour_index_torxtamperproof], True)
                    approx = cv2.approxPolyDP(contours_torxtamperproof[Max_contour_index_torxtamperproof], epsilon, True)
                    torxtamperproof_approx_area = cv2.contourArea(approx)
                    torxtamperproof_approx_arcLength = cv2.arcLength(approx, True)
                    if torxtamperproof_approx_arcLength > 80 and torxtamperproof_approx_area < 450.5:
                        torxtamperproof_approx_arcLength = 80.292929

                elif classnumber in ['square', 'slotted', 'triangle']:
                    mask = np.zeros(Threshold_Image.shape, dtype='uint8')
                    # self.Histogram = cv2.bitwise_and(inputimage, maskimage, inputimage)
                    cv2.circle(mask, center, radius_int, (255, 255, 255), -1)
                    new_image = cv2.bitwise_and(inputimage, mask)
                    # self.Histogram = new_image[center[1]-radius_int:center[1]+radius_int, center[0]-radius_int:center[0]+radius_int]
                    self.Histogram = mask
                    mean_value = cv2.mean(new_image[center[1] - radius_int:center[1] + radius_int,
                                          center[0] - radius_int:center[0] + radius_int])
                    threshold_value = int(mean_value[0]*1.1)
                    # print(f'mean_value = {mean_value[0]} mean_value\' = {threshold_value}')
                    ret, Threshold_Image_mean_value = cv2.threshold(inputimage, threshold_value, 255, cv2.THRESH_BINARY)
                    # self.Histogram = Threshold_Image_mean_value
                    contours_square,_ = cv2.findContours(cv2.bitwise_and(Threshold_Image_mean_value, maskimage), cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_NONE)
                    Max_contour_index_square = self.FindMaxContours_For_torxtamperproof(contours_square)
                    square_area = cv2.contourArea(contours_square[Max_contour_index_square])
                    cv2.drawContours(self.InputImage, contours_square, Max_contour_index_square, (99, 242, 50), 1)
                    # 近似轮廓
                    epsilon = 0.05 * cv2.arcLength(contours_square[Max_contour_index_square], True)
                    approx = cv2.approxPolyDP(contours_square[Max_contour_index_square], epsilon, True)
                    cv2.drawContours(self.InputImage, [approx], -1, (0, 0, 255), 1)
                    vertices = len(approx)
                    # print(f'vertices up = {classnumber} {vertices}')
                else:
                    self.Histogram = maskimage
                    cv2.circle(self.InputImage, center, radius_int, (255, 0, 0), 1)

                # 获取轮廓的顶点数
                # print((radius*2)*22*0.001)
                # print(min(rect[1][:])*22*0.001)
                # print(max(rect[1][:])*22*0.001)
                # GaussianBlur = cv2.cvtColor(GaussianBlur, cv2.COLOR_GRAY2BGR)  # 圖像存儲使用8-8-8 24位RGB格式
                radius = round(radius * 2 * 22 * 0.001, 3)#54.55
                # cv2.imwrite(f'./Measure/{classnumber}_{radius}.png', Threshold_Image)
                if classnumber in ['torx', 'pentalope', 'torxtamperproof']:
                    # 近似轮廓
                    if classnumber in ['pentalope'] and radius < 0.377:
                        epsilon = 0.045 * cv2.arcLength(contours[max_idx], True)
                    else:
                        epsilon = 0.04 * cv2.arcLength(contours[max_idx], True)
                    approx = cv2.approxPolyDP(contours[max_idx], epsilon, True)
                    cv2.drawContours(self.InputImage, [approx], -1, (0, 0, 255), 1)
                    vertices = len(approx)
                elif classnumber in ['triangle', 'phillips', 'slotted']:
                    # 近似轮廓
                    epsilon = 0.05 * cv2.arcLength(contours[max_idx], True)
                    approx = cv2.approxPolyDP(contours[max_idx], epsilon, True)
                    cv2.drawContours(self.InputImage, [approx], -1, (0, 0, 255), 1)
                    vertices = len(approx)
                    # print(f'vertices under = {classnumber} {vertices}')
                elif classnumber in ['triwing']:
                    epsilon = 0.07 * cv2.arcLength(contours[max_idx], True)
                    approx = cv2.approxPolyDP(contours[max_idx], epsilon, True)
                    cv2.drawContours(self.InputImage, [approx], -1, (0, 0, 255), 1)
                    vertices = len(approx)

                aspect_ratios = self.draw_min_rect(self.InputImage, contours, max_idx)
                if classnumber in ['torxtamperproof']:
                    return self.InputImage, radius, torxtamperproof_approx_arcLength, torxtamperproof_approx_area
                # elif classnumber in ['square', 'slotted', 'triangle']:
                #     return self.InputImage, radius, square_area, vertices
                else:
                    # if classnumber in ['square', 'slotted', 'triangle']:
                        # print(f'aspect_ratios = {classnumber} {aspect_ratios}')
                    return self.InputImage, radius, aspect_ratios, vertices
            else:
                return self.InputImage, 0, 0, 0
        else:
            return self.measure_for_KleinTool(classnumber)
            # return self.AI_measure_for_KleinTool(classnumber)
    def measure_for_KleinTool(self, classnumber):
        if len(self.InputImage.shape) == 3:
            inputimage = cv2.cvtColor(self.InputImage, cv2.COLOR_BGR2GRAY)  # 圖像存儲使用8-8-8 24位RGB格式
        else:
            inputimage = copy.deepcopy(self.InputImage)
            self.InputImage = cv2.cvtColor(self.InputImage, cv2.COLOR_GRAY2BGR)
        # GaussianBlur = cv2.GaussianBlur(inputimage, (31, 31), 0)

        self.Remedy = inputimage
        self.Histogram = inputimage
        if classnumber == 'spanner' or classnumber == '03_Spanner':
            inputimage = self.Unsharpen(inputimage)
            maskimage = self.GetMask_for_KleinTool(inputimage, 55, 60)
            maskimage_spanner = self.GetMask_for_KleinTool(inputimage, 80, 60)

            self.Histogram = maskimage
            ret, Threshold_Image = cv2.threshold(inputimage, 205, 255, cv2.THRESH_BINARY)
            cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
            self.Remedy = Threshold_Image
        elif classnumber == 'square':
            ret, Threshold_Image = cv2.threshold(inputimage, 130, 255, cv2.THRESH_BINARY)
        elif classnumber == 'hextamperproof':
            inputimage = self.Unsharpen(inputimage)
            self.Remedy = inputimage
            maskimage = self.GetMask_for_KleinTool(inputimage)
            self.Histogram = maskimage
            ret, Threshold_Image = cv2.threshold(inputimage, 140, 255, cv2.THRESH_BINARY)
            cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
        elif classnumber == 'triwing':
            ret, Threshold_Image = cv2.threshold(inputimage, 170, 255, cv2.THRESH_BINARY)  # 150
        elif classnumber == 'torxtamperproof':
            inputimage = self.Unsharpen(inputimage)
            self.Remedy = inputimage
            maskimage = self.GetMask_for_KleinTool(inputimage, 55)
            self.Histogram = maskimage
            Get_MeanValue = cv2.mean(cv2.bitwise_and(inputimage, maskimage))[0]  # 計算套頭形狀部分的亮度平均值
            # print(f'第一次平均值 = {Get_MeanValue}')
            ret, Threshold_Image = cv2.threshold(inputimage, 115, 255, cv2.THRESH_BINARY)  # 150
            cv2.bitwise_and(Threshold_Image, maskimage, Threshold_Image)
            cv2.imwrite(f'./Measure/1_Threshold_Image.png', Threshold_Image)
        else:
            ret, Threshold_Image = cv2.threshold(inputimage, 180, 255, cv2.THRESH_BINARY)#150
        contours, _ = cv2.findContours(Threshold_Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if classnumber in ['hextamperproof']:
            max_idx = self.FindMaxContours(contours)
            cv2.drawContours(self.InputImage, contours, -1, (99, 242, 50), 1)
        elif classnumber in ['torxtamperproof']:
            max_idx = self.FindMaxContours_For_torxtamperproof(
                contours, 150)  # 找最大輪廓
        else:
            max_idx = self.FindMaxContours_For_Other(contours, 150)

        if max_idx > -1:
            vertices = 0
            (x, y), radius = cv2.minEnclosingCircle(contours[max_idx])
            center = (int(x), int(y))
            radius_int = int(radius)
            if classnumber in ['torxtamperproof']:
                mask = np.zeros(Threshold_Image.shape, dtype='uint8')
                cv2.circle(mask, center, radius_int, (255, 255, 255), -1)
                cv2.circle(self.InputImage, center, radius_int, (0, 0, 255), 2)
                new_image = cv2.bitwise_and(inputimage, mask)
                # cv2.imwrite(f'./Measure/new_image.png', new_image)
                mean_value = cv2.mean(new_image[center[1] - radius_int:center[1] + radius_int,center[0] - radius_int:center[0] + radius_int])  # 計算套頭形狀部分的亮度平均值
                threshold_value = int(mean_value[0] * 1.15)  # 計算inputimage的閾值
                # print(f'threshold_value = {threshold_value}')
                self.Histogram = cv2.bitwise_and(new_image, maskimage)
                ret, Threshold_Image_mean_value = cv2.threshold(cv2.bitwise_and(new_image, maskimage),threshold_value, 255, cv2.THRESH_BINARY)  # 二值化
                # self.Histogram = new_image
                contours_torxtamperproof, _ = cv2.findContours(Threshold_Image_mean_value, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)# 找輪廓
                Max_contour_index_torxtamperproof = self.FindMaxContours_For_torxtamperproof(contours_torxtamperproof)  # 找最大輪廓
                # cv2.drawContours(self.InputImage, inner_class, -1, (99, 242, 50), 1)
                (x, y), radius = cv2.minEnclosingCircle(contours_torxtamperproof[Max_contour_index_torxtamperproof])  # 找最大輪廓最小外接園的直徑和圓心
                center = (int(x), int(y))
                radius_int = int(radius)
                cv2.circle(self.InputImage, center, radius_int, (0, 242, 255), 1)
            elif classnumber in ['hextamperproof']:
                mask = np.zeros(Threshold_Image.shape, dtype='uint8')
                cv2.circle(mask, center, radius_int - 3, (255, 255, 255), -1)
                cv2.circle(self.InputImage, center, radius_int - 3, (0, 0, 255), 2)

                new_image = cv2.bitwise_and(inputimage, mask)
                new_image = cv2.add(new_image, cv2.bitwise_not(mask))
                cv2.imwrite(f'./Measure/new_image.png', new_image)
                x_start = center[0] - radius_int if center[0] - radius_int >= 0 else 0
                y_start = center[1] - radius_int if center[1] - radius_int >= 0 else 0
                x_end = center[0] + radius_int if center[0] + radius_int < Threshold_Image.shape[0] else Threshold_Image.shape[0]-1
                y_end = center[1] + radius_int if center[1] + radius_int < Threshold_Image.shape[0] else Threshold_Image.shape[0]-1

                mean_value = cv2.mean(inputimage[y_start:y_end, x_start:x_end])  # 計算套頭形狀部分的亮度平均值
                # print(f'mean_value = {mean_value}')
                threshold_value = int(mean_value[0] * 0.9)  # 計算inputimage的閾值
                # print(f'threshold_value = {threshold_value}')
                ret, Threshold_Image_mean_value = cv2.threshold(new_image, threshold_value, 255,cv2.THRESH_BINARY)  # 二值化
                self.Histogram = Threshold_Image_mean_value
                contours_hextamperproof, _ = cv2.findContours(cv2.bitwise_not(Threshold_Image_mean_value), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)# 找輪廓
                # i = 0
                # hierach_id = 0
                # inner_class = []
                # try:
                #     while not (contours_hextamperproof[2][0][i][2] == -1) and contours_hextamperproof[2][0][i][1] == -1 and i < len(contours_hextamperproof[1]) and not (contours_hextamperproof[2][0][i][3] == -1):
                #         hierach_id = i
                #         i += 1
                # except:
                #     cv2.imwrite(f'./Measure/error.png', Threshold_Image_mean_value)
                # while not (contours_hextamperproof[2][0][hierach_id][0] == -1):
                #     inner_class.append(contours_hextamperproof[1][hierach_id])
                #     hierach_id = contours_hextamperproof[2][0][hierach_id][0]


                Max_contour_index_hextamperproof = self.FindMaxContours_For_hextamperproof(contours_hextamperproof, 10)  # 找最大輪廓
                # print(f'Max_contour_index_hextamperproof = {Max_contour_index_hextamperproof}')
                # cv2.drawContours(self.InputImage, contours_hextamperproof, -1, (99, 242, 50), 1)
                try:
                    (x, y), radius = cv2.minEnclosingCircle(
                        contours_hextamperproof[Max_contour_index_hextamperproof])  # 找最大輪廓最小外接園的直徑和圓心
                    # print(f'area = {cv2.contourArea(contours_hextamperproof[Max_contour_index_hextamperproof])}')
                except:
                    cv2.imwrite(f'./Measure/error_minEnclosingCircle.png', Threshold_Image_mean_value)

                center = (int(x), int(y))
                radius_int = int(radius)
                cv2.circle(self.InputImage, center, radius_int, (0, 242, 255), 1)
            elif classnumber == 'spanner':
                new_image = cv2.bitwise_and(inputimage, maskimage)
                ret, Threshold_Image_Overcircle = cv2.threshold(cv2.bitwise_and(inputimage, maskimage_spanner), 200,
                                                                255, cv2.THRESH_BINARY)  # 二值化
                ret, Threshold_Image_extend = cv2.threshold(new_image, 230, 255, cv2.THRESH_BINARY)  # 二值化
                kernal = np.ones((9, 9), np.uint8)

                Threshold_Image_extend = cv2.morphologyEx(Threshold_Image_extend, cv2.MORPH_DILATE, kernel=kernal,
                                                          iterations=3)

                new_image = cv2.bitwise_or(new_image,
                                           cv2.bitwise_and(Threshold_Image_extend, Threshold_Image_Overcircle))

                mean_value = cv2.mean(new_image[center[1] - radius_int:center[1] + radius_int,
                                      center[0] - radius_int:center[0] + radius_int])  # 計算套頭形狀部分的亮度平均值
                threshold_value = int(mean_value[0] * 0.9)  # 計算inputimage的閾值
                # print(f'threshold_value = {threshold_value}')
                self.Histogram = new_image
                self.Remedy = Threshold_Image_Overcircle
                self.extend = Threshold_Image_extend

                ret, Threshold_Image_mean_value = cv2.threshold(new_image, threshold_value,
                                                                255, cv2.THRESH_BINARY)  # 二值化
                cv2.imwrite(f'./Measure/Threshold_Image_mean_value.png', Threshold_Image_mean_value)
                kernal = np.ones((3, 3), np.uint8)

                Threshold_Image_mean_value = cv2.morphologyEx(Threshold_Image_mean_value, cv2.MORPH_OPEN, kernel=kernal,
                                                              iterations=1)
                Threshold_Image_mean_value = cv2.morphologyEx(Threshold_Image_mean_value, cv2.MORPH_CLOSE,
                                                              kernel=kernal, iterations=3)

                # correct_value = correct(Threshold_Image)
                # rotate_image = rotate(Threshold_Image, correct_value, center)
                x_projection = abs(
                    np.sort([k for k, x in enumerate(np.sum(Threshold_Image_mean_value, axis=0)) if x > 0])[-1] -
                    np.sort([k for k, x in enumerate(np.sum(Threshold_Image_mean_value, axis=0)) if x > 0])[0])
                y_projection = abs(
                    np.sort([k for k, x in enumerate(np.sum(Threshold_Image_mean_value, axis=1)) if x > 0])[-1] -
                    np.sort([k for k, x in enumerate(np.sum(Threshold_Image_mean_value, axis=1)) if x > 0])[0])

                # count_zero_pixels = (Threshold_Image == 255).sum()
                # print(count_zero_pixels)
                return Threshold_Image_mean_value, math.sqrt(
                    (x_projection * x_projection + y_projection * y_projection)), x_projection, y_projection

            else:
                self.Histogram = Threshold_Image
                cv2.circle(self.InputImage, center, radius_int, (255, 0, 0), 1)
                radius = round(radius * 2 * 22 * 0.001, 3)  # 54.55
                aspect_ratios = self.draw_min_rect(self.InputImage, contours, max_idx)
                return self.InputImage, radius, aspect_ratios, vertices
            # radius = round(radius * 2 * 22 * 0.001, 3)  # 54.55
            return self.InputImage, radius, 29, vertices

        else:
            self.Histogram = maskimage
            return self.InputImage, 0, 0, 0
    def GetMask(self, image):
        ret, maskimage = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY_INV)#75
        self.Histogram = maskimage
        contours, _ = cv2.findContours(maskimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        max_idx = self.FindMaxContours(contours)

        if max_idx > -1:
            (x, y, w, h) = cv2.boundingRect(contours[max_idx])
            mask = np.zeros(maskimage.shape, dtype='uint8')
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.imwrite(f'./Measure/maskimage.png', mask)
            return mask
        else:
            print('errer --> GetMask')
            return []
    def GetMask_for_KleinTool(self, image, max_size=65, threshold_value=75):
        ret, maskimage = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(maskimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        max_idx = self.FindMaxContours(contours)
        if max_idx > -1:
            mask = np.zeros(maskimage.shape, dtype='uint8')
            (x, y), radius = cv2.minEnclosingCircle(contours[max_idx])
            center = (int(x), int(y))
            radius_int = int(radius)
            # print(f'GetMask_for_KleinTool --> radius_int = {radius_int}')
            cv2.circle(mask, center, max_size, (255, 255, 255), -1)
            # cv2.drawContours(mask, contours, max_idx, (255, 255, 255), -1)
            cv2.imwrite(f'./Measure/maskimage.png', mask)
            return mask
        else:
            # self.dev_logger.error(f'GetMask_for_KleinTool max_idx == -1')
            print('error --> GetMask')
            return []
    def Get_area(self, Threshold_img, x, y, radius):
        mask = np.zeros(Threshold_img.shape, dtype='uint8')
        center = (int(x), int(y))
        radius_int = int(radius)
        cv2.circle(mask, center, radius_int, (255, 255, 255), -1)
        new_image = cv2.bitwise_and(cv2.bitwise_not(Threshold_img), mask)
        cv2.imwrite(f'./Measure/new_image.png', new_image)
    def Unsharpen(self, inputimage):
        # USM锐化增强方法(Unsharpen Mask)
        # 先对原图高斯模糊，用原图减去系数x高斯模糊的图像
        # 再把值Scale到0~255的RGB像素范围
        # 优点：可以去除一些细小细节的干扰和噪声，比卷积更真实
        # （原图像-w*高斯模糊）/（1-w）；w表示权重（0.1~0.9），默认0.6

        # sigma = 5、15、25
        blur_img = cv2.GaussianBlur(inputimage, (0, 0), 5)
        usm = cv2.addWeighted(inputimage, 1.5, blur_img, -0.5, 0)
        # cv.addWeighted(图1,权重1, 图2, 权重2, gamma修正系数, dst可选参数, dtype可选参数)

        h, w = inputimage.shape[:2]
        result = np.zeros([h, w * 2], dtype=inputimage.dtype)
        result[0:h, 0:w] = inputimage
        result[0:h, w:2 * w] = usm
        # cv.putText(图像名，标题，（x坐标，y坐标），字体，字的大小，颜色，字的粗细）
        return usm
    def HighPassFilter(self, src):
        # 傅立叶变化
        src_dft = cv2.dft(np.float32(src), flags=cv2.DFT_COMPLEX_OUTPUT)
        # 将图片中心从左上角移到中心
        src_dft_shift = np.fft.fftshift(src_dft)

        # 制作掩膜令中心为0,后面才能过滤掉中心低频
        rows, cols = src.shape
        crow, ccol = int(rows / 2), int(cols / 2)
        mask = np.ones((rows, cols, 2), np.uint8)
        mask_size = 3
        mask[crow - mask_size:crow + mask_size, ccol - mask_size:ccol + mask_size] = 0

        # 用掩膜对图像进行处理
        src_dft_shift_over = src_dft_shift * mask

        # 将中心移回左上角
        src_dft_shift_over_ishift = np.fft.ifftshift(src_dft_shift_over)

        # 傅立叶逆变换
        src_dft_shift_over_ishift_idft = cv2.idft(src_dft_shift_over_ishift)

        # 后续操作,将矢量转换成标量,并映射到合理范围之内
        src_dft_shift_over_ishift_idft = cv2.magnitude(src_dft_shift_over_ishift_idft[:, :, 0],
                                                       src_dft_shift_over_ishift_idft[:, :, 1])
        src_dft_shift_over_ishift_idft = np.abs(src_dft_shift_over_ishift_idft)
        src_dft_shift_over_ishift_idft = (src_dft_shift_over_ishift_idft - np.amin(src_dft_shift_over_ishift_idft)) / (
                    np.amax(src_dft_shift_over_ishift_idft) - np.amin(src_dft_shift_over_ishift_idft))
        # src_dft_shift_over_ishift_idft = cv2.normalize(src_dft_shift_over_ishift_idft, 0, 255, cv2.NORM_MINMAX)
        # print(src_dft_shift_over_ishift_idft)
        return (src_dft_shift_over_ishift_idft * 255).astype('uint8')
    def FindMaxContours_For_torxtamperproof(self, contours, size=100):
        try:
            # 計算輪廓面積
            area = [cv2.contourArea(contour) for contour in contours]
            # 找到前三大的面積的索引
            max_indices = np.argsort(np.array(area))[::-1][:3]
            # 取得前三大的輪廓
            max_contours = [contours[i] for i in max_indices if cv2.contourArea(contours[i]) > 100]
            # 計算每個輪廓的重心
            centroids = []
            for contour in max_contours:
                moments = cv2.moments(contour)
                # 檢查面積是否為非零值，避免除以零的情況
                if moments["m00"] != 0:
                    cx = moments["m10"] / moments["m00"]
                    cy = moments["m01"] / moments["m00"]
                    centroids.append(np.array([cx, cy]))
            # 計算每個輪廓的重心距離影像中心的距離
            center = np.array([size / 2, size / 2])  # 替換成你的影像寬高
            distances = [np.linalg.norm(centroid - center) for centroid in centroids]
            # 找到最近的輪廓索引
            closest_idx = np.argmin(np.array(distances))
            # 找到最近的輪廓在前三大輪廓中的索引
            final_idx = max_indices[closest_idx]
        except Exception as e:
            # self.dev_logger.error(f'FindMaxContours_For_torxtamperproof {e}')
            final_idx = -1
            print(f'FindMaxContours_For_torxtamperproof --> {e}')
        return final_idx
    def FindMaxContours_For_Other(self, contours, size=100):
        try:
            # 計算輪廓面積
            area = [cv2.contourArea(contour) for contour in contours]
            # 找到前三大的面積的索引
            max_indices = np.argsort(np.array(area))[::-1][:6]
            # 取得前三大的輪廓
            max_contours = [contours[i] for i in max_indices if cv2.contourArea(contours[i]) > 20]
            # 計算每個輪廓的重心
            centroids = []
            for contour in max_contours:
                moments = cv2.moments(contour)
                # 檢查面積是否為非零值，避免除以零的情況
                if moments["m00"] != 0:
                    cx = moments["m10"] / moments["m00"]
                    cy = moments["m01"] / moments["m00"]
                    centroids.append(np.array([cx, cy]))

            # 計算每個輪廓的重心距離影像中心的距離
            center = np.array([size / 2, size / 2])  # 替換成你的影像寬高
            distances = [np.linalg.norm(centroid - center) for centroid in centroids]

            # 找到最近的輪廓索引
            closest_idx = np.argmin(np.array(distances))

            # 找到最近的輪廓在前三大輪廓中的索引
            final_idx = max_indices[closest_idx]

        except Exception as e:
            # self.dev_logger.error(f'FindMaxContours_For_Other {e}')
            final_idx = -1
            print(f'FindMaxContours_For_Other --> {e}')

        return final_idx
    def FindMaxContours_For_hextamperproof(self, contours, size=20):
        try:
            # 計算輪廓面積
            area = [cv2.contourArea(contour) for contour in contours]
            # 找到前三大的面積的索引
            max_indices = np.argsort(np.array(area))[::-1][:3]

            # 取得前三大的輪廓
            max_contours = [i for i in max_indices if cv2.contourArea(contours[i]) > 6]

            for max_i in max_contours:
                # 使用最小外接圓擬合輪廓
                (x, y), radius = cv2.minEnclosingCircle(contours[max_i])
                # print(radius)
                # 檢查直徑是否在指定範圍內
                if radius <= 40 and area[max_i] > size:
                    return max_i
            final_idx = max_contours[-1]
        except Exception as e:
            # self.dev_logger.error(f'FindMaxContours_For_hextamperproof {e}')
            final_idx = -1
            print(f'FindMaxContours_For_hextamperproof --> {e}')

        return final_idx
    def FindMaxContours(self, contours):
        try:
            area = []
            for contour in contours:
                area.append(cv2.contourArea(contour))
            max_idx = np.argmax(np.array(area))
        except Exception as e:
            # self.dev_logger.error(f'FindMaxContours {e}')
            max_idx = -1
            print(f'FindMaxContours --> {e}')
        return max_idx
    def draw_min_rect(self, image, contours, max_idx):
        aspect_ratio = 29
        try:
            if max_idx > -1:
                # Get the minimum bounding rectangle
                rect = cv2.minAreaRect(contours[max_idx])
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                # Draw the rectangle on the image
                # cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

                # Calculate and print the aspect ratio
                width = np.linalg.norm(box[0] - box[1])
                height = np.linalg.norm(box[1] - box[2])
                if width > height:
                    temp = height
                    height = width
                    width = temp

                if height == 0:
                    aspect_ratio = 1
                else:
                    aspect_ratio = width / height
                # print(f'Minimum Bounding Rectangle Aspect Ratio: {aspect_ratio}')

                return aspect_ratio
            else:
                print('error --> draw_min_rect')
                return 29
        except Exception as e:
            # self.dev_logger.error(f'draw_min_rect\n {e}')
            return 29


class ROI_Data:
    def __init__(self, image, y_start, y_stop, x_start, x_stop):
        self.Image = image
        self.Y_start = y_start
        self.Y_stop = y_stop
        self.X_start = x_start
        self.X_stop = x_stop

class Image_and_Index:
    def __init__(self, image, index):
        self.Image = image
        self.Image_Index = index

class image_k_file_img:
    def __init__(self, k, file, img_filename,  img):
        self.Image_Index = k
        self.file = file
        self.img_filename = img_filename
        self.Image = img
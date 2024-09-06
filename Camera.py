import configparser

from pypylon import pylon
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableWidgetItem, QHeaderView, QHBoxLayout
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject
class Camera(QThread):
    FreeRun = pyqtSignal()
    def __init__(self):
        super().__init__()
        try:
            self.ExposureTime_List = list()
            self.GetExposureTime()
            self.cam = self.search_get_device()
            self.cam.Open()
            # self.cam.Width = 5472
            # self.cam.Height = 3648
            self.cam.Width = 3400
            self.cam.Height = 1852
            self.Width = self.cam.Width.GetValue()
            self.Height = self.cam.Height.GetValue()
            # self.cam.OffsetX = 0#936
            # self.cam.OffsetY = 0#542
            self.cam.OffsetX = 936#936
            self.cam.OffsetY = 542#886
            self.cam.Gain = 14.95698
            self.cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


            self.Image_RealTime = []
            self.Camera_isOpen = True
            # self.Image_RealTime = cv2.imread(r"D:\ScrewdriverData\1201TranningSetAI\origin\2023_12_01_15_44_18.png", cv2.IMREAD_COLOR)
        except Exception as e:
            print('相機連線失敗')
            print(e)
            self.Camera_isOpen = False

    def Recipe_Change(self, recipe):
        config = configparser.ConfigParser()
        config.read('ScrewDrive.ini')
        number_list = config['Camera_Offset'][f'{recipe}'].split(',')
        int_numbers = [int(number) for number in number_list]
        self.cam.OffsetX = int_numbers[0]  # 936
        self.cam.OffsetY = int_numbers[1]  # 886
        print(f'Camera_Offset_Change--> {int_numbers}')
        # if recipe == 'KleinTool':
        #     self.cam.ReverseX.SetValue(True)


    def Get_CameraTemperature(self):
        node_map = self.cam.GetNodeMap()
        # 获取温度节点
        temperature_node = node_map.GetNode('DeviceTemperature')
        temperature = temperature_node.GetValue()
        # print(f"Camera temperature: {temperature} °C")
        return temperature
    def run(self):
        while self.cam.IsGrabbing():
            grabResult = self.cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                # Access the image data.
                image = self.converter.Convert(grabResult)
                self.Image_RealTime = image.GetArray()
                self.FreeRun.emit()
            grabResult.Release()
        self.cam.Close()
    def search_get_device(self):
        tl_factory = pylon.TlFactory.GetInstance()
        for dev_info in tl_factory.EnumerateDevices():
            print("DeviceClass", dev_info.GetDeviceClass())
            if dev_info.GetDeviceClass() == "BaslerUsb":
                print(f"ModelName:{dev_info.GetModelName()}\n",f"IP:{dev_info.GetIpAddress()}")
                camera = pylon.InstantCamera(tl_factory.CreateDevice(dev_info))
                break
        else:
            raise EnvironmentError("no BaslerUsb device found")
        return camera

    def Grab(self):
        grabResult = self.cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        weld_img = []
        if grabResult.GrabSucceeded():
            image = self.converter.Convert(grabResult)
            weld_img = image.GetArray()
        return weld_img

    def SetExposureTime(self, exposuretime):
        self.cam.ExposureTime.SetValue(exposuretime)  # 100000 microsecond

    def GetExposureTime(self):
        config = configparser.ConfigParser()
        config.read('ScrewDrive.ini')
        for key in config['ExposureTime']:
            self.ExposureTime_List.append(config['ExposureTime'][key])
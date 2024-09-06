import configparser
import sys
import wmi

class Lock():
    def __init__(self, dev_logger=None):
        self.computer = wmi.WMI()
        self.Lock_Motherboard_serial_number = ''
        self.Read_Lock_Information()
        self.dev_logger = dev_logger

        if self.Get_Motherboard_serial_number() == '07D2511_L91E628468':  # 好像是4060
            print('你是對的電腦')
        elif self.Get_Motherboard_serial_number() == '180733062600115':  # 我的電腦
            print('你是對的電腦')
        elif self.Get_Motherboard_serial_number() == '230723303501125':
            print('你是對的電腦')
        else:
            print(f'你是錯的電腦')
            self.dev_logger.info('你是錯的電腦')
            sys.exit()

    def Read_Lock_Information(self):
        config = configparser.ConfigParser()
        config.read('ScrewDrive.ini')
        self.Lock_Motherboard_serial_number = config['Lock']['Motherboard_serial_number']

    def Get_Motherboard_serial_number(self):
        # 主板序列号
        cc = ""
        for board_id in self.computer.Win32_BaseBoard():
            # print(board_id.SerialNumber)
            cc += board_id.SerialNumber
        return cc
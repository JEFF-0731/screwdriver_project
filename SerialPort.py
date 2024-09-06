import serial
import time
import numpy as np

class SerialPort:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.port = "COM3"

        # 115200,N,8,1
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE  # set parity check
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits

        self.ser.timeout = 0.5  # non-block read 0.5s
        self.ser.writeTimeout = 0.5  # timeout for write 0.5s
        self.ser.xonxoff = False  # disable software flow control
        self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control

        # write 8 byte data
        self.com1_Status = False
        self.com2_Status = False
        self.com3_Status = False
        self.com4_Status = False

        self.time_Delay = 0.05
        # # write 8 byte data
        # self.com1_on_Status = b"\x01\x05\x00\x00\xff\x00\x8c\x3a"
        # self.com2_on_Status = b"\x01\x05\x00\x01\xff\x00\xdd\xfa"
        # self.com3_on_Status = b"\x01\x05\x00\x02\xff\x00\x2d\xfa"
        # self.com4_on_Status = b"\x01\x05\x00\x03\xff\x00\x7c\x3a"
        #
        # self.com1_off_Status = b"\x01\x05\x00\x00\x00\x00\xcd\xca"
        # self.com2_off_Status = b"\x01\x05\x00\x01\x00\x00\x9c\x0a"
        # self.com3_off_Status = b"\x01\x05\x00\x02\x00\x00\x6c\x0a"
        # self.com4_off_Status = b"\x01\x05\x00\x03\x00\x00\x3d\xca"
    def io_Control(self,io_States):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com1_on(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x00\xff\x00\x8c\x3a"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com2_on(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x01\xff\x00\xdd\xfa"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com3_on(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x02\xff\x00\x2d\xfa"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com4_on(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x03\xff\x00\x7c\x3a"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com1_off(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x00\x00\x00\xcd\xca"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com2_off(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x01\x00\x00\x9c\x0a"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
    def com3_off(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x02\x00\x00\x6c\x0a"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")

    def com4_off(self):
        try:
            self.ser.open()
        except Exception as ex:
            print("open serial port error " + str(ex))
            exit()

        if self.ser.isOpen():

            try:
                self.ser.flushInput()  # flush input buffer
                self.ser.flushOutput()  # flush output buffer
                io_States = b"\x01\x05\x00\x03\x00\x00\x3d\xca"
                self.ser.write(np.array(bytearray(io_States)))
                time.sleep(self.time_Delay)  # wait 0.5s
                self.ser.close()
            except Exception as e1:
                print("communicating error " + str(e1))

        else:
            print("open serial port error")
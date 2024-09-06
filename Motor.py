import serial  # 引用pySerial模組
from time import sleep


class Motor:
   def __init__(self):
       self.COM_PORT = 'COM3'  # 指定通訊埠名稱
       self.BAUD_RATES = 9600  # 設定傳輸速率
       self.Motor_isOpen = False
       self.Motor_isForwards = True
       self.motor_idle_time = 0  # 設定馬達閒置平台移進去時間
       try:
           self.ser = serial.Serial(self.COM_PORT, self.BAUD_RATES)  # 初始化序列通訊埠
           self.Motor_isOpen = True
       except Exception as e:
           print(e)
           print('馬達未連接')

   def Move(self):
       if self.Motor_isOpen:
           self.motor_idle_time = 0
           if self.Motor_isForwards:
               self.ser.write(b'MF\n')  # 訊息必須是位元組類型
               self.Motor_isForwards = False
               print('Motor Forward')
           else:
               self.ser.write(b'MB\n')  # 訊息必須是位元組類型
               self.Motor_isForwards = True
               print('Motor Backward')
           sleep(0.7)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('馬達未連接')

   def MotorInit(self):
       if self.Motor_isOpen:
           self.ser.write(b'H\n')  # 訊息必須是位元組類型
           sleep(0.5)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()
               print('控制板回應：', mcu_feedback)
       else:
           print('馬達未連接')

   def Green(self):
       if self.Motor_isOpen:
           self.ser.write(b'Green\n')  # 訊息必須是位元組類型
           sleep(0.7)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('Arduino未連接')

   def Yellow(self):
       if self.Motor_isOpen:
           self.ser.write(b'Yellow\n')  # 訊息必須是位元組類型
           sleep(0.7)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('Arduino未連接')

   def Red(self):
       if self.Motor_isOpen:
           self.ser.write(b'Red\n')  # 訊息必須是位元組類型
           sleep(0.7)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('Arduino未連接')

   def Buzzer(self):
       if self.Motor_isOpen:
           self.ser.write(b'Buzzer\n')  # 訊息必須是位元組類型
           sleep(0.7)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('Arduino未連接')
   def Off(self):
       if self.Motor_isOpen:
           self.ser.write(b'Off\n')  # 訊息必須是位元組類型
           sleep(0.5)
           while self.ser.in_waiting:
               mcu_feedback = self.ser.readline().decode()  # 接收回應訊息並解碼
               print('控制板回應：', mcu_feedback)
       else:
           print('Arduino未連接')



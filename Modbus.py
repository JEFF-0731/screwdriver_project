import socket
import threading
import time
#ping 192.168.0.105 -t
class Modbus:
    def __init__(self, dev_logger=None):
        self.dev_logger = dev_logger

        self.server_ip = '192.168.0.105'
        self.server_port = 10001
        self.time_delay = 0.03
        self.io_state = [0x00]

        # write 8 byte data
        self.com1_Status = False
        self.com2_Status = False
        self.com3_Status = False
        self.com4_Status = False
        self.com2andcom3_Status = False

        self.modbus_reconnect_time = 0#設定IO卡閒置重新連線時間

        # 在初始化中进行连接
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_full_addr = (self.server_ip, self.server_port)
        try:
            self.sock.connect(server_full_addr)
            self.Modbus_isOpen = True
            self.CloseModbus = False

            threading.Thread(target=self.reconnect_periodically, args=(900,)).start()
            self.dev_logger.info('IO卡連線成功')
        except:
            print('IO卡連線失敗')
            self.dev_logger.error('IO卡連線失敗')
            self.Modbus_isOpen = False

        print("Connected to the server successfully.")
        self.com_all_off()

    # Function to convert bytes to a hexadecimal string
    def byte_to_hex_str(self, byte_array, length):
        return ' '.join(['{:02X}'.format(b) for b in byte_array[:length]])
    def close_connection(self):
        self.sock.close()

    def reconnect_periodically(self, interval):
        self.dev_logger.info('IO reconnect_periodically Start')
        while True:
            for i in range(0, interval):
                time.sleep(1)  # 等待一段时间
                if self.CloseModbus:
                    break
            if self.CloseModbus:
                break
            self.Modbus_isOpen = False
            time.sleep(10)  # 等待當前計算結束
            self.close_connection()  # 关闭连接
            time.sleep(3)  # 可选的延迟，确保连接关闭
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_full_addr = (self.server_ip, self.server_port)
                self.sock.connect(server_full_addr)
                self.Modbus_isOpen = True
                print("Reconnected to the server.")
                self.dev_logger.info('IO Reconnected to the server')

            except Exception as e:
                print('Failed to reconnect:', str(e))
                self.Modbus_isOpen = False
                self.dev_logger.error(f'Failed to reconnect: {str(e)}')
        self.dev_logger.info('IO reconnect_periodically End')


    def control_com(self):
        try:
            self.modbus_reconnect_time = 0#有對IO進行通訊，把重新連線計時器歸0
            # Build the message for the 8-channel open command
            byte_message = bytearray()
            # TID - Transfer Identifier
            byte_message.extend([0x00, 0x00])
            # PID - Protocol Identifier (default is 0)
            byte_message.extend([0x00, 0x00])
            # Number of bytes to follow (0x08)
            byte_message.extend([0x00, 0x08])
            # UID - Modbus module address
            byte_message.extend([0x01])
            # MODBUS command number (0x0f for writing multiple discrete outputs)
            byte_message.extend([0x0f])
            # Start address for writing (Y1 address is 0x0000)
            byte_message.extend([0x00, 0x00])
            # Number of outputs to operate (8)
            byte_message.extend([0x00, 0x08])
            # Number of bytes following (0x01)
            byte_message.extend([0x01])
            # Data for the 8 channels
            byte_message.extend(self.io_state * 8)
            # Send the message
            self.sock.send(byte_message)
            # Receive data
            # message_rcv = self.sock.recv(1024)
            # Display received data as a hexadecimal string
            # print("Received data: ", self.byte_to_hex_str(message_rcv, len(message_rcv)))
            time.sleep(self.time_delay)
        except Exception as ee:
            print("Failed to connect to the server:", str(ee))
            self.dev_logger.error(f'Failed to connect to the server: {str(ee)}')

        # finally:
        #     time.sleep(self.time_delay)
        #     self.sock.close()
    def com_all_on(self):
        # print(self.io_state)
        self.io_state = [16]
        # print(self.io_state)
        self.control_com()
    def com_all_off(self):
        # print(self.io_state)
        self.io_state = [0]
        # print(self.io_state)
        self.control_com()
    def com1_on(self):
        # print(self.io_state)
        self.io_state = [a + 0x01 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com2_on(self):
        # print(self.io_state)
        self.io_state = [a + 0x02 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com2andcom3_on(self):
        # print(self.io_state)
        self.io_state = [a + 0x06 for a in self.io_state]
        print(self.io_state)
        self.control_com()
    def com3_on(self):
        # print(self.io_state)
        self.io_state = [a + 0x04 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com4_on(self):
        # print(self.io_state)
        self.io_state = [a + 0x08 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com1_off(self):
        # print(self.io_state)
        self.io_state = [a - 0x01 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com2_off(self):
        # print(self.io_state)
        self.io_state = [a - 0x02 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com2andcom3_off(self):
        # print(self.io_state)
        self.io_state = [a - 0x06 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com3_off(self):
        # print(self.io_state)
        self.io_state = [a - 0x04 for a in self.io_state]
        # print(self.io_state)
        self.control_com()
    def com4_off(self):
        # print(self.io_state)
        self.io_state = [a - 0x08 for a in self.io_state]
        # print(self.io_state)
        self.control_com()

if __name__ == '__main__':
    modbus = Modbus()
    modbus.com1_on()
    modbus.com2_on()
    modbus.com3_on()
    modbus.com4_on()
    time.sleep(5)
    modbus.com1_off()
    modbus.com2_off()
    modbus.com3_off()
    modbus.com4_off()


import serial
import time
import threading
import struct

# 동작 상수
ALIVE = 0
DIGITAL = 1
ANALOG = 2
PWM = 3
SERVO_PIN = 4
TONE = 5
PULSEIN = 6
ULTRASONIC = 7
TIMER = 8
NEOPIXEL = 14
NEOPIXELCLEAR = 15
NEOPIXELINIT = 16
NEOPIXELRAINBOW = 17
NEOPIXELEACH = 18
TEMPCHECK = 22

# 상태 상수
GET = 1
SET = 2
RESET = 3


def data_to_hex(data):
    """바이트 데이터를 HEX 형식의 문자열로 변환"""
    return ' '.join(f'{byte:02X}' for byte in data)


def parse_serial_data(data):
    """
    Parse the given serial data and return the float value if it is ULTRASONIC data.

    Parameters:
    - data: bytes, the serial data received

    Returns:
    - float value if the data is for ULTRASONIC, None otherwise
    """

    # Define constants
    START_BYTES = b'\xff\x55'
    FLOAT_TYPE = b'\x02'
    ULTRASONIC_DEVICE = b'\x07'
    TEMP_DEVICE = b'\x16'

    # Check if data starts with the start bytes
    if not data.startswith(START_BYTES):
        return None

    # Extract data type, float bytes, and device type
    data_type = data[2:3]
    float_bytes = data[3:7]
    device_type_temp = data[8:9]
    device_type = data[9:10]

    if data_type == FLOAT_TYPE :
        if device_type == ULTRASONIC_DEVICE:  # Check if data type is float and device type is ULTRASONIC
            # Convert the bytes to float and return
            return struct.unpack('<f', float_bytes)[0]
        elif device_type_temp == TEMP_DEVICE:  
            return struct.unpack('<f', float_bytes)[0]
    return None


class ArduinoCommunicator:
    def __init__(self, port, baudrate=38400):
        self.serial = serial.Serial(port, baudrate)
        self.prefix = [0xFF, 0x55]
        self.ultra_distance = 0
        self.temp = 0
        self.stop_event = threading.Event()  # 이벤트 추가
        self.read_thread = threading.Thread(target=self.read_data_loop)
        self.read_thread.daemon = True  # 메인 스레드가 종료되면 자동으로 종료되도록 설정
        self.read_thread.start()

    def close(self):
        """Terminate the reading thread and close the serial connection"""
        self.stop_event.set()  # 종료 신호 보내기
        if self.read_thread.is_alive():
            self.read_thread.join()  # Wait for the thread to finish
        self.serial.close()

    def __del__(self):
        """Destructor - called when an instance is about to be destroyed"""
        self.close()

    def __enter__(self):
        """For use with 'with' statement"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """For use with 'with' statement"""
        self.close()

    def read_data_loop(self):
        while not self.stop_event.is_set():
            try:
                # 헤더를 검색하여 데이터를 읽습니다.
                data_before_header = self.serial.read_until(bytes(self.prefix))

                # 헤더 이후로 개행 문자가 나올 때까지 데이터를 읽습니다.
                data_after_header = b""
                while not data_after_header.endswith(b'\r\n') and not self.stop_event.is_set():
                    data_after_header += self.serial.read(1)  # 한 바이트씩 읽기

                # 헤더 전과 후의 데이터를 합칩니다.
                accumulated_data = data_before_header + data_after_header
                
                dist = parse_serial_data(accumulated_data)
                
                if dist is not None:
                    self.ultra_distance = dist
                    self.temp = dist

            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break

    def send_command(self, bytes_command):
        """Send a series of bytes to the Arduino"""
        self.serial.write(bytes_command)

    def move_servo(self, pin, angle):
        """
        Move a servo on the given pin to the specified angle.
        """
        if not (0 <= angle <= 180):
            raise ValueError("Angle should be between 0 and 180 degrees.")

        # Adjusted command structure as you mentioned
        bytes_command = bytes(self.prefix + [5, 0x0, SET, SERVO_PIN, pin, angle])
        self.send_command(bytes_command)

    def set_digital(self, pin, value):
        """
        Set a digital pin to HIGH or LOW.
        """
        if value not in [0, 1]:
            raise ValueError("Value should be 0 (LOW) or 1 (HIGH)")

        bytes_command = bytes(self.prefix + [5, 0x0, SET, DIGITAL, pin, value])
        self.send_command(bytes_command)

    def set_pwm(self, pin, value):
        """
        Send a PWM signal to a specified pin.
        """
        if not (0 <= value <= 255):
            raise ValueError("PWM value should be between 0 and 255")

        bytes_command = bytes(self.prefix + [5, 0x0, SET, PWM, pin, value])
        self.send_command(bytes_command)

    def set_tone(self, pin, frequency, duration):
        """
        Play a tone on a specified pin.
        """
        # Assuming frequency is 16 bits and duration is 16 bits.
        bytes_command = bytes(
            self.prefix + [7, 0x0, 2, 5, pin, frequency & 0xFF, frequency >> 8, duration & 0xFF, duration >> 8])
        self.send_command(bytes_command)

    def get_ultrasonic(self, trig=6, echo=5):
        # Assuming frequency is 16 bits and duration is 16 bits.
        bytes_command = bytes(
            self.prefix + [5, 0x00, GET, ULTRASONIC, trig, echo])
        self.send_command(bytes_command)

    def get_temp(self):
        # Assuming frequency is 16 bits and duration is 16 bits.
        bytes_command = bytes(
            self.prefix + [3, 0x00, GET, TEMPCHECK])
        self.send_command(bytes_command)    


# 사용 예제
# with ArduinoCommunicator(port='COM3') as arduino:
#     arduino.move_servo(pin=9, angle=90)
#     arduino.set_digital(pin=13, value=1)
#     arduino.set_pwm(pin=6, value=128)
#     arduino.set_tone(pin=10, frequency=440, duration=1000)


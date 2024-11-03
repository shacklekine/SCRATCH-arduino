import serial
import serial.tools.list_ports
import time

HEADER = b'\xFF\x55'

def find_arduino_port( baudrate=38400, timeout=2, retries=3,  wait_time=3):
    """
    header: 확인할 프로토콜 헤더
    baudrate: 시리얼 통신 속도 (기본값 115200)
    timeout: 포트 읽기 시 타임아웃 (기본값 1초)
    search_duration: 각 포트에서 검색할 시간 (기본값 2초)
    retries: 각 포트를 검사하는 시도 횟수 (기본값 3회)
    """

    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"Checking port: {p.device}")  # 포트 이름 출력
        accumulated_data = bytearray()  # 누적된 데이터를 저장할 변수
        for _ in range(retries):  # 여러 번 시도
            try:
                with serial.Serial(p.device, baudrate, timeout=timeout) as ser:
                    time.sleep(wait_time)  # 데이터가 충분히 도착할 때까지 대기
                    while ser.in_waiting:
                        accumulated_data += ser.read(ser.in_waiting)  # 버퍼에 있는 모든 데이터 읽기

                    if HEADER in accumulated_data:  # 누적된 데이터 내에서 헤더 검색
                        print(f"Connection Successful on {p.device}")
                        return p.device
            except serial.SerialException:
                pass

    print(f"No available ports for connection")
    return None
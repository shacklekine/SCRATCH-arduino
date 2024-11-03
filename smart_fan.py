from LIB.arduinoCommunicator import ArduinoCommunicator
from LIB.arguinoPortChecker import find_arduino_port
from datetime import datetime, timezone
import time
import mysql.connector
import requests



temp_url = "http://43.203.78.172:8080/arduino/temp-data"
humi_url = "http://43.203.78.172:8080/arduino/humi-data"
post_url = "http://43.203.78.172:8080/arduino/data"

result_data = {}

port = find_arduino_port()                          # 자동으로 아두이노와 연결할 port를 찾는 함수
arduino = ArduinoCommunicator(port)                 # 아두이노와 통신하기 위한 라이브러리 초기화

fan_r = 9 #inba
fan_l = 13
r_pin = 3
g_pin = 5
b_pin = 6
   

try:
    response = requests.get(temp_url)
    print("start")
    if response.status_code == 200:
        print("POST 요청 성공!")
        response_data = response.json() #응담 data를 json으로 파싱
        """"
        #Value 값을 json에서 가져와 변환
        value = int(response_data["result"]["value"])
        print(f"value 값: {value}")
        """

        result = response_data["result"]

        result_data['id'] = result['id']
        result_data['deviceId'] = result['deviceId']
        result_data['tagName'] = result['tagName']
        result_data['value'] = result['value']
        

    else:
        print(f"POST 요청 실패! 상태코드: {response.status_code}")

except requests.exceptions.RequestException as e :
    print(f"요청 중 오류 발생:{e}")

print("저장된 데이터:", result_data)

if 'value' in result_data and result_data['value'] > 50:
    print(f"Value detected")
    value_trigger = 1
else:
    print(f"Value failed")


while ('value' in result_data and result_data['value'] > 20):
    time.sleep(1)
    arduino.get_temp()
    print( f"{arduino.temp:.2f}")  

    if  ((arduino.temp > 30)):                          # 온도가 30도 이상이면 (온도 기준값 바꿔도 됩니다.)
        arduino.set_pwm(r_pin, 125)                    # LED 불빛 표현 r,g,b   
        arduino.set_pwm(g_pin, 0)
        arduino.set_pwm(b_pin, 0)
        arduino.set_pwm(fan_r, 225) 

        now = datetime.now(timezone.utc)
        time_string = now.isoformat()
        time_string_with_z = time_string.replace('+00:00', 'Z')
        print(time_string_with_z)


        try:
            post_data = {
                "time" : time_string_with_z,
                "temperature" : arduino.temp

            }

            post_response = requests.post(post_url, json=post_data)

            if post_response.status_code == 200:
                print("success!")
            else:
                print("failed..")
        except requests.exceptions.RequestException as e:
            print(f"POST 요청 중 오류 발생:{e}")
                

    else:
        arduino.set_pwm(r_pin, 0)                  # LED 불빛 표현 r,g,b   
        arduino.set_pwm(g_pin, 125)
        arduino.set_pwm(b_pin, 0)
        arduino.set_pwm(fan_r, 100) 





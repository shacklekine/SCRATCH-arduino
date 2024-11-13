from LIB.arduinoCommunicator import ArduinoCommunicator
from LIB.arguinoPortChecker import find_arduino_port
from datetime import datetime, timezone
import time
import mysql.connector
import requests

#"http://43.203.78.172:8080/arduino/data"

temp_url = "http://43.203.72.254:8080/arduino/temp-data"
humi_url = "http://43.203.72.254:8080/arduino/humi-data"
post_url = "http://43.203.72.254:8080/arduino/data"
current_url = "http://43.203.72.254:8080/arduino/current-data"

result_data = {}
result_h_data = {}
result_c_data = {}

port = find_arduino_port()                          # 자동으로 아두이노와 연결할 port를 찾는 함수
arduino = ArduinoCommunicator(port)                 # 아두이노와 통신하기 위한 라이브러리 초기화

fan_r = 9 #inba
fan_l = 13
r_pin = 3
g_pin = 5
b_pin = 6

humi_trigger = ('value' in result_h_data and result_h_data['value'] > 50)
temp_trigger = (arduino.temp > 30)   

try:
    response = requests.get(temp_url)
    print("start")
    if response.status_code == 200:
        print("POST 요청 성공!")
        response_data = response.json() #응담 data를 json으로 파싱

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

try:
    response_h = requests.get(humi_url)
    print("start")
    if response_h.status_code == 200:
        print("POST 요청 성공!")
        response_h_data = response_h.json() #응담 data를 json으로 파싱
        
        result_h = response_h_data["result"]

        result_h_data['id'] = result_h['id']
        result_h_data['deviceId'] = result_h['deviceId']
        result_h_data['tagName'] = result_h['tagName']
        result_h_data['value'] = result_h['value']
        

    else:
        print(f"POST 요청 실패! 상태코드: {response_h.status_code}")

except requests.exceptions.RequestException as e :
    print(f"요청 중 오류 발생:{e}")

print("저장된 데이터:", result_h_data)

if 'value' in result_h_data and result_h_data['value'] > 50:
    print(f"Value_h detected")
    value_trigger = 1
else:
    print(f"Value_h failed")



current_count = 0

#시작 트리거 설정
while ('value' in result_data and result_data['value'] > 0):
    time.sleep(30)
    arduino.get_temp()
    print( f"{arduino.temp:.2f}")  


    ################################


    now_0 = datetime.now(timezone.utc)
    time_string_0 = now_0.isoformat()
    time_string_with_z_0 = time_string_0.replace('+00:00', 'Z')
    print(time_string_with_z_0)


    try:
        current_data = {
            "time" : time_string_with_z_0,
            "current" : current_count

        }

        post_response = requests.post(current_url, json=current_data)

        if post_response.status_code == 200:
            print("c_success!")
        else:
            print("c_failed..")
    except requests.exceptions.RequestException as e:
        print(f"c_POST 요청 중 오류 발생:{e}")
                


    if 'value' in result_h_data and result_h_data['value'] > 30:    #습도 트리거 변경 지점
       humi_detected = 1
    else:
       humi_detected = 0


    if ((humi_detected == 1) and (arduino.temp > 25)):
        value_trigger = 2
    elif(((humi_detected == 0) and (arduino.temp > 25)) or ((humi_detected == 1) and (arduino.temp < 25))):
        value_trigger = 1    
    else:
        value_trigger = 0





    if  (value_trigger == 2):                          # 온도가 30도 이상이면 (온도 기준값 바꿔도 됩니다.)
        arduino.set_pwm(r_pin, 125)                    # LED 불빛 표현 r,g,b   
        arduino.set_pwm(g_pin, 0)
        arduino.set_pwm(b_pin, 0)
        arduino.set_pwm(fan_r, 225) 
#
        current_count += 11000

        now = datetime.now(timezone.utc)
        time_string = now.isoformat()
        time_string_with_z = time_string.replace('+00:00', 'Z')
        print(time_string_with_z)

        value_trigger = 0

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
                
    elif(value_trigger == 1):
        arduino.set_pwm(r_pin, 0)                  # LED 불빛 표현 r,g,b   
        arduino.set_pwm(g_pin, 0)
        arduino.set_pwm(b_pin, 125)
        arduino.set_pwm(fan_r, 150) 
        value_trigger = 0
        current_count += (11000 * (150/225))

    else:
        arduino.set_pwm(r_pin, 0)                  # LED 불빛 표현 r,g,b   
        arduino.set_pwm(g_pin, 125)
        arduino.set_pwm(b_pin, 0)
        arduino.set_pwm(fan_r, 100) 
        value_trigger = 0
        current_count += (11000 * (100/225))

















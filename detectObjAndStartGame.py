# 소리 출력 및 시리얼 통신, 서버 통신
import serial
import pygame
import time
import requests
import json

# 객체인식 모듈 
import cv2
import numpy as np

print("file open")

# 카메라 열기
thresh = 50 # 픽셀이 변화된 갯수 25개의 픽셀이 변화 (움직임 정도 설정)
max_diff = 5
 
cap=cv2.VideoCapture(-1,cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

# 스타트 플레그
start_flag = 0

# sound load
pygame.mixer.init()

mugung1 = pygame.mixer.Sound("1sec_mugunghwa.wav")
mugung2 = pygame.mixer.Sound("2sec_mugunghwa.wav")
mugung3 = pygame.mixer.Sound("3sec_mugunghwa.wav")
success = pygame.mixer.Sound("success.wav")
fail = pygame.mixer.Sound("fail.wav")

# serial load
ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
ser.flush()

# 객체인식 함수정의
def detectObject(thresh, max_diff) :
    global a, b, c
    print("함수안")
    a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    c_gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)

    diff1 = cv2.absdiff(a_gray, b_gray)
    diff2 = cv2.absdiff(b_gray, c_gray)

    ret, diff1_t = cv2.threshold(diff1, thresh, 255, cv2.THRESH_BINARY)
    ret, diff2_t = cv2.threshold(diff2, thresh, 255, cv2.THRESH_BINARY)

    diff = cv2.bitwise_and(diff1_t, diff2_t)

    k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, k)
    diff_cnt = cv2.countNonZero(diff)
    if diff_cnt > max_diff:
        nzero = np.nonzero(diff)
        cv2.rectangle(draw, (min(nzero[1]), min(nzero[0])),
                      (max(nzero[1]), max(nzero[0])), (0, 255, 0), 2)

        cv2.putText(draw, "Motion detected!!", (10, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))
        print("실패맨")
        fail.play()
        ser.write(bytes('s', encoding='ascii'))
        while True :
            line = ser.readline().decode('utf-8').rstrip()
            if line == 's' :
                break
        time.sleep(3.0)
        quit()
        # 움직임 감지시 API로 String이나 Int 형식으로 데이터 넘기기
        #requests.post('http://203.250.32.29:1817/home/motiondect', {'detecting': 1})
    stacked = np.hstack((draw, cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)))
    cv2.imshow('motion', stacked)

    a = b
    b = c


a, b, c = None, None, None # a,b,c 3개의 프레임

# Send start signal to arduino
while True :
    ser.write(bytes('g', encoding='ascii'))
    line = ser.readline().decode('utf-8').rstrip()
    if line == 'g' :
        break

# In game
if cap.isOpened():  
    ret, a = cap.read()
    ret, b = cap.read()
    while ret:
        ret, c = cap.read()
        draw = c.copy()
        if not ret:
            break
        
        # 움직임 감지
        detectObject(thresh,max_diff)
        
        if ser.in_waiting > 0 :
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            if line == 'p1' :
                mugung1.play()
                time.sleep(1.4)
            elif line == 'p2' :
                mugung2.play()
                time.sleep(2.5)
            elif line == 'p3' :
                mugung3.play()
                time.sleep(3.2)
            elif line == 'intrrupt!' :
                sec = ser.readline().decode('utf-8').rstrip()
                sec = float(sec)
                success.play()
                requests.post('http://203.250.32.29:1817/home/record', {'recordScore':sec})
                time.sleep(3.0)
                print(sec)
                break
            
        




'''
# 원본 코드
while True :
    if ser.in_waiting > 0 :
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        if line == 'p1' :
            mugung1.play()
            time.sleep(1.0)
        elif line == 'p2' :
            mugung2.play()
            time.sleep(2.0)
        elif line == 'p3' :
            mugung3.play()
            time.sleep(1.0)
        elif line == 'intrrupt!' :
            sec = ser.readline().decode('utf-8').rstrip()
            sec = float(sec)
            success.play()
            requests.post('http://203.250.32.29:1817/home/record', {'recordScore':sec})
            time.sleep(3.0)
            print(sec)
            break
'''
 ###############################################################################################################


 

 


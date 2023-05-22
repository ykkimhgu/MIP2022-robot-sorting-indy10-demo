from indy_utils import indydcp_client as client
from indy_utils.indy_program_maker import JsonProgramComponent

import json
import threading
from time import sleep
import numpy as np
import random

import pyzbar.pyzbar as pyzbar
import cv2

import subprocess
import sys

import serial
import time

# Indy와 연결된 와이파이 IP와 모델명을 입력
robot_ip = "192.168.0.6"    # Robot (Indy) IP
robot_name = "NRMK-Indy10"  # Robot name (Indy10) Indy

# IP와 모델명을 통해 Indy를 선언
indy = client.IndyDCPClient(robot_ip, robot_name)

# Indy와 연결
indy.connect()

# Indy 세팅
indy.set_collision_level(5)
indy.set_joint_vel_level(3)
indy.set_task_vel_level(3)
indy.set_joint_blend_radius(20)
indy.set_task_blend_radius(0.2)

# Arduino Uno 세팅
py_serial = serial.Serial(
    
    # Windows 포트
    port='COM4',
    
    # 보드 레이트 (통신 속도)
    baudrate=9600,
)

# Indy의 상태를 key에 저장
key = []
status = indy.get_robot_status()
for value in status.keys():
    key.append(value)

# Indy의 상태를 확인하는 함수를 선언
def check_operation(x):
    while True:  
        status = indy.get_robot_status()
        sleep(0.2)
        if status[key[5]]==1 :
            break
    if type(x) == int:
        print('done : move %d process' % x)
    elif type(x) == str:
        print('done : %s process' % x)

# 부품 종류에 따라 움직일 방향 및 거리를 알려주는 함수를 선언
def part_direction(part_list):
    side_move = 0
    if part_list[0] == 'A':
        side_move = 0.225
    elif part_list[0] == 'B':
        side_move = -0.235
    return side_move

# 숫자가 중복되는지 확인하는 함수를 선언
def check_num(num, list):
  conf = 0
  if num not in list:
    conf = 1
  return conf

# 난수를 통해 숫자 리스트를 만드는 함수를 선언
def random_list(x):
  new_list = []
  for i in range(0,x):
    if i == 0 :
      new_list.append(random.randint(1,x))
    else :
      new_num = random.randint(1,x)
      while check_num(new_num, new_list) == 0:
        new_num = random.randint(1,x)
      new_list.append(new_num)
  return new_list

# 부품을 종류에 맞게 분류한 리스트를 만드는 함수를 선언
def part_classify(list, a):
  total = len(list)
  for i in range(0, total):
    if list[i] <= a:
      list[i] = 'A' + str(list[i])
    elif list[i] > a:
      list[i] = 'B' + str(list[i]-a)
  return list

# 프로그램 실행 시 먼저 home 위치로 가서 대기
indy.go_home()

# Indy가 동작한 후에는 꼭 이 구문을 넣어줌으로써 오류를 방지
check_operation('home')

power_on = 1                      # Indy의 작동이 필요한 경우: 1, Indy의 작동이 필요없는 경우: 0

part_list = list(range(4))        # 부품 목록을 저장
part_location = list(range(4))    # 부품의 위치를 저장

new_part_list = list(range(4))    # 새로운 부품 목록을 저장

commend = str(0)                  # 아두이노 명령 선언

while(1):
    
    # QR List를 'qr_code_reader.py'파일에서 읽음
    out = subprocess.check_output(['python', 'qr_code_reader.py'])
    qr_list = out.decode('utf-8')

    # 각 파트의 QR 값을 저장         
    part_list[0] = qr_list[:2]
    part_list[1] = qr_list[2:4]
    part_list[2] = qr_list[4:6]
    part_list[3] = qr_list[6:8]

    # 작동 명령어를 저장
    move_com = qr_list[8:len(qr_list)-2]

    # Indy에 작동 명령이 떨어진 경우
    if move_com == 'Move':
        print('Part Sequence : ', part_list[0], part_list[1], part_list[2], part_list[3], '\n')
        commend = 'b'
    # Indy에 정지 명령이 떨어진 경우
    elif move_com == 'Stop':
        power_on = 0

    # 시작 위치를 설정
    start_pos = [0.75474, 0.00010, 0.60269, 179.97, 1.18, 179.92]
    
    if power_on == 1:
        # Sequence 1: 나열된 4개의 부품을 종류 별로 분류
        for cnt in range(0, len(part_list)):
            # 1단계: 부품 위로 이동
            print('\n', "현재 시퀀스", cnt, '\n')
            start_pos_copy = [0.75474, 0.00010, 0.60269, 179.97, 1.18, 179.92]
            start_pos_copy[0] -= (0.05 * cnt)
            indy.task_move_to(start_pos_copy)

            check_operation(1)

            # 2단계: z축 방향으로 내려가서 부품을 집을 준비를 마침
            t_pos = indy.get_task_pos()
            t_pos[2] -= 0.055
            indy.task_move_to(t_pos)

            check_operation(2)

            # 3단계: Vaccum head를 통해 부품을 집음
            indy.set_do(10, 1)
            indy.set_do(11, 0)       
                  
            check_operation(3)

            # 4단계: 부품을 집은 채 z축 방향으로 올라감
            t_pos[2] += 0.055
            indy.task_move_to(t_pos)

            check_operation(4)

            # 5단계: 부품을 집은 채 종류에 따라 해당 위치로 움직임
            t_pos[1] += part_direction(part_list[cnt])
            indy.task_move_to(t_pos)

            check_operation(5)

            part_location[cnt] = t_pos

            # 6단계: 부품을 집은 채 z축 방향으로 내려감
            t_pos[2] -= 0.113
            indy.task_move_to(t_pos)

            check_operation(6)

            # 7단계: Vaccum head를 통해 부품을 놓음
            indy.set_do(10, 0)
            indy.set_do(11, 1)       
                  
            check_operation(7)

            # 8단계: 부품을 놓은 채 z축 방향으로 올라감
            t_pos[2] += 0.113
            indy.task_move_to(t_pos)

            check_operation(8)
        
        # Sequence 2: 난수 알고리즘을 통해 새로운 부품 배열 순서 생성
        # 1~4 사이의 난수로 리스트 생성
        new_part_list = random_list(4)

        # 생성된 리스트를 부품 리스트로 변환
        new_part_list = part_classify(new_part_list, 2)
        
        # 새로운 부품 배열 순서를 출력
        print('New Part Sequence : ', new_part_list[0], new_part_list[1], new_part_list[2], new_part_list[3], '\n')

        match_num = 0
        
        # Sequence 3: 새로운 부품 배열 순서에 맞게 부품 배열
        for i in range(0, len(new_part_list)):
            print('\n', "현재 시퀀스", i, '\n')
            for j in range(0, len(part_list)):
                if new_part_list[i] == part_list[j]:
                    match_num = j

            # 1단계: 부품 위로 이동
            indy.task_move_to(part_location[match_num])

            check_operation(1)

            # 2단계: z축 방향으로 내려가서 부품을 집을 준비를 마침
            t_pos = indy.get_task_pos()
            t_pos[2] -= 0.113
            indy.task_move_to(t_pos)

            check_operation(2)

            # 3단계: Vaccum head를 통해 부품을 집음
            indy.set_do(10, 1)
            indy.set_do(11, 0)       
                  
            check_operation(3)

            # 4단계: 부품을 집은 채 z축 방향으로 올라감
            t_pos[2] += 0.113
            indy.task_move_to(t_pos)

            check_operation(4)

            # 5단계: 부품을 집은 채 정해진 위치로 움직임
            part_pos = [0.75474, 0.00010, 0.60269, 179.97, 1.18, 179.92]
            part_pos[0] -= (0.05 * i)
            indy.task_move_to(part_pos)

            check_operation(5)

            # 6단계: 부품을 집은 채 z축 방향으로 내려감
            part_pos[2] -= 0.055
            indy.task_move_to(part_pos)

            check_operation(6)

            # 7단계: Vaccum head를 통해 부품을 놓음
            indy.set_do(10, 0)
            indy.set_do(11, 1)       
                  
            check_operation(7)

            # 8단계: 부품을 놓은 채 z축 방향으로 올라감
            part_pos[2] += 0.055
            indy.task_move_to(part_pos)

            check_operation(8)

        # 시퀀스 모두 완료 시 시작 위치로 간 뒤 home 위치로 복귀 후 대기
        indy.task_move_to(start_pos)
        
        check_operation('start')

        indy.go_home()

        check_operation('home')

        # 시리얼 통신으로 컨베이어 벨트에게 명령
        py_serial.write(commend.encode())
    
        time.sleep(0.1)

        # 컨베이어 벨트의 답장을 출력
        if py_serial.readable():
          response = py_serial.readline()
          print(response[:len(response)-1].decode())
  
    if power_on == 0:
        # 추가적인 기계 작동이 없는 것으로 판단하고 zero 위치로 복귀
        indy.go_zero()

        check_operation('zero')

        # 기계 연결을 해제
        indy.disconnect()

        # 프로그램을 종료
        sys.exit()
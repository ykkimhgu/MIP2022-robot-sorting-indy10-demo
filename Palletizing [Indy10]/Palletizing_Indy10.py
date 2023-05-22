from indy_utils import indydcp_client as client
from indy_utils.indy_program_maker import JsonProgramComponent

import json
import threading
from time import sleep
import numpy as np

import pyzbar.pyzbar as pyzbar
import cv2

import subprocess
import sys

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

# 다음 순서의 좌표를 계산하는 함수를 선언
def next_pos_cal(cur_pos, cur_seq):
    # 우체국 상자 2호 규격 : 270[mm] x 180[mm] x 150[mm]
    # [0] : x좌표, [1]: y좌표, [2]: z좌표
    if cur_seq == 1:
        cur_pos[0] += 0.005
        cur_pos[1] -= 0.277
    elif cur_seq == 2:
        cur_pos[0] += 0.180
        cur_pos[1] += 0.279
    elif cur_seq == 3:
        cur_pos[1] -= 0.285
    elif cur_seq == 4:
        cur_pos[0] -= 0.185
        cur_pos[1] += 0.283
        cur_pos[2] += 0.15
    # 계산된 다음 순서의 좌표를 반환    
    return cur_pos

# 프로그램 실행 시 먼저 home 위치로 가서 대기
indy.go_home()

# Indy가 동작한 후에는 꼭 이 구문을 넣어줌으로써 오류를 방지
check_operation('home')

power_on = 1   # Indy의 작동이 필요한 경우: 1, Indy의 작동이 필요없는 경우: 0

layer = 1      # 물류 층
seq = 0        # 팔레타이징 순서

while(1):
    
    # Palletizing command를 'box_detecter.py'파일에서 읽음
    out = subprocess.check_output(['python', 'box_detecter.py'])
    palletiz_com = out.decode('utf-8')              
    move_com = palletiz_com[:4]                         
    box_angle = palletiz_com[5:len(palletiz_com)-2]

    # box_angle
    if move_com == 'Move' and int(box_angle) >= 85 :
        box_angle = str(0)

    # palletiz_com에 저장된 입력값을 출력
    print('\n', 'Palletizing Command : ', move_com, '\n')
    print('Box Angle : ', box_angle, '\n')

    # Indy에 작동 명령이 떨어진 경우
    if move_com == 'Move':
        seq = seq + 1
        # Palletizing 형식을 정함 (2x2 or 3x3)
        # 2x2인 경우에는 seq == 5, 3x3인 경우에는 seq == 10
        if seq == 5:
            seq = 1
            layer = layer + 1
        # Palletizing layer & sequence를 출력
        print('Palletizing Layer : ', layer, '\n')
        print('Palletizing Sequence : ', seq, '\n')
    # Indy에 정지 명령이 떨어진 경우
    elif move_com == 'Stop':
        power_on = 0

    # 최초의 Palletizing 좌표를 설정
    # 다음 순서의 Palletizing 좌표는 next_pos_cal() 함수를 통해 계산
    if layer == 1 and seq == 1:
        locate_pos = [0.71925, 0.17725, 0.22942, 0.75, 176.55, 5.62]
    
    if power_on == 1:
        # 1단계: 상자가 놓여지는 고정된 위치의 위로 이동
        t_pos = [0.09766, -0.49899, 0.62613, 179.88, 1.51, 96.72]
        indy.task_move_to(t_pos)

        check_operation(1)
        
        # 2단계: 상자의 각도에 맞게 헤드(6번 조인트)를 회전
        j_pos = indy.get_joint_pos()
        j_pos[5] = j_pos[5] + int(box_angle)
        indy.joint_move_to(j_pos)
        
        check_operation(2)
        
        # 3단계: z축 방향으로 내려가서 상자를 집을 준비를 마침
        t_pos2 = indy.get_task_pos()
        t_pos2[2] -= 0.15
        indy.task_move_to(t_pos2)

        check_operation(3)

        # 4단계: Vaccum head를 통해 상자를 집음
        indy.set_do(10, 1)
        indy.set_do(11, 0)       
               
        check_operation(4)

        # 5단계: 상자를 집은 채 z축 방향으로 올라감
        t_pos2 = indy.get_task_pos()
        t_pos2[2] += 0.15
        indy.task_move_to(t_pos2)

        check_operation(5)

        # 6단계: 상자를 집은 채 1단계 위치로 복귀
        indy.task_move_to(t_pos)
        
        check_operation(6)

        # 7단계: home 위치로 이동
        indy.go_home()      
        
        check_operation(7)

        # 8단계: Palletizing Sequence에 해당되는 위치의 위로 이동
        indy.task_move_to(locate_pos)

        check_operation(8)

        # 9단계: z축 방향으로 내려가서 상자를 놓을 준비를 마침
        locate_pos[2] -= 0.145
        indy.task_move_to(locate_pos)

        check_operation(9)

        # 10단계: Vaccum head를 통해 상자를 놓음
        indy.set_do(10, 0)
        indy.set_do(11, 1)
        
        check_operation(10)

        # 11단계: z축 방향으로 다시 올라감
        locate_pos[2] += 0.145
        indy.task_move_to(locate_pos)

        check_operation(11)

        # 12단계: home 위치로 돌아가서 대기
        indy.go_home()

        check_operation(12)

        # 다음 순서의 Palletizing 좌표를 설정
        locate_pos = next_pos_cal(locate_pos, seq)

    if power_on == 0:
        # 추가적인 기계 작동이 없는 것으로 판단하고 zero 위치로 복귀
        indy.go_zero()

        check_operation('zero')

        # 기계 연결을 해제
        indy.disconnect()

        # 프로그램을 종료
        sys.exit()
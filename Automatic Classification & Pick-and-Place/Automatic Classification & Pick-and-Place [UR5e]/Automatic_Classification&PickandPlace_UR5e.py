from urx import Robot
from math import pi

from time import sleep
import random

import subprocess
import sys

# UR5e와 연결된 IP를 입력하여 UR5e와 연결
rob = Robot("192.168.0.2")

# UR5e 세팅
acc = 0.5       # 정확도
vel = 0.2       # 속도

# UR5e의 상태를 확인하는 함수를 선언
def check_operation(x):
    while True:  
        sleep(0.2)
        if rob.is_program_running() is not True :
            break
    if type(x) == int:
        print('done : move %d process' % x)
    elif type(x) == str:
        print('done : %s process' % x)

# 부품 종류에 따라 움직일 방향을 알려주는 함수를 선언
def part_direction(part_list):
    side_move = 0
    if part_list[0] == 'A':
        side_move = 0.10
    elif part_list[0] == 'B':
        side_move = -0.10
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

# 프로그램 실행 시 먼저 ~~ 위치로 가서 대기
### 설정 필요

# UR5e가 동작한 후에는 꼭 이 구문을 넣어줌으로써 오류를 방지
check_operation('home')

power_on = 1          # IR5e의 작동이 필요한 경우: 1, UR5e의 작동이 필요없는 경우: 0

part_list = []        # 부품 목록을 저장
part_location = []    # 부품의 위치를 저장

new_part_list = []    # 새로운 부품 목록을 저장

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

    # UR5e에 작동 명령이 떨어진 경우
    if move_com == 'Move':
        print('Part Sequence : ', part_list[0], part_list[1], part_list[2], part_list[3], '\n')
    # UR5e에 정지 명령이 떨어진 경우
    elif move_com == 'Stop':
        power_on = 0

    # 시작 위치를 설정
    start_pos = [] ### 설정 필요
    
    if power_on == 1:
        # Sequence 1: 나열된 4개의 부품을 종류 별로 분류
        for cnt in range(0, len(part_list)):
            # 1단계: 부품 위로 이동
            start_pos_copy = start_pos
            start_pos_copy.pos.x -= (0.15 * cnt) ### 수정 필요
            rob.set_pose(start_pos_copy, acc=0.5, vel=0.2, wait=False)

            check_operation(1)

            # 2단계: z축 방향으로 내려가서 부품을 집을 준비를 마침
            t_pos = rob.get_pose()
            t_pos.pos.z -= 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(2)

            # 3단계: RG2 Gripper를 통해 부품을 집음
   
            #       
            #check_operation(3)

            # 4단계: 부품을 집은 채 z축 방향으로 올라감
            t_pos.pos.z += 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(4)

            # 5단계: 부품을 집은 채 종류에 따라 해당 위치로 움직임
            t_pos[1] += part_direction(part_list[cnt])
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(5)

            part_location[cnt] = t_pos

            # 6단계: 부품을 집은 채 z축 방향으로 내려감
            t_pos.pos.z -= 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(6)

            # 7단계: RG2 Gripper를 통해 부품을 놓음
       
            #       
            #check_operation(7)

            # 8단계: 부품을 놓은 채 z축 방향으로 올라감
            t_pos.pos.z += 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(8)
        
        # Sequence 2: 난수 알고리즘을 통해 새로운 부품 배열 순서 생성
        # 1~4 사이의 난수로 리스트 생성
        new_part_list = random_list(4)

        # 생성된 리스트를 부품 리스트로 변환
        new_part_list = part_classify(new_part_list, 2)
        
        match_num = 0
        
        # Sequence 3: 새로운 부품 배열 순서에 맞게 부품 배열
        for i in range(0, len(new_part_list)):
            for j in range(0, len(part_list)):
                if new_part_list[i] == part_list[j]:
                    match_num = j

            # 1단계: 부품 위로 이동
            rob.set_pose(part_location[match_num], acc=0.5, vel=0.2, wait=False)

            check_operation(1)

            # 2단계: z축 방향으로 내려가서 부품을 집을 준비를 마침
            t_pos = rob.get_pose()
            t_pos.pos.z -= 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(2)

            # 3단계: RG2 Gripper를 통해 부품을 집음
                   
            #       
            #check_operation(3)

            # 4단계: 부품을 집은 채 z축 방향으로 올라감
            t_pos.pos.z += 0.15
            rob.set_pose(t_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(4)

            # 5단계: 부품을 집은 채 정해진 위치로 움직임
            part_pos = start_pos
            part_pos.pos.x -= (0.15 * i) ### 수정 필요
            rob.set_pose(part_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(5)

            # 6단계: 부품을 집은 채 z축 방향으로 내려감
            part_pos.pos.z -= 0.15
            rob.set_pose(part_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(6)

            # 7단계: RG2 Gripprt를 통해 부품을 놓음
     
            #       
            #check_operation(7)

            # 8단계: 부품을 놓은 채 z축 방향으로 올라감
            part_pos.pos.z += 0.15
            rob.set_pose(part_pos, acc=0.5, vel=0.2, wait=False)

            check_operation(8)

    if power_on == 0:
        # 추가적인 기계 작동이 없는 것으로 판단하고 zero 위치로 복귀
        indy.go_zero() ### 설정 필요

        check_operation('zero')

        # UR5e와의 연결을 해제
        rob.close()

        # 프로그램을 종료
        sys.exit()
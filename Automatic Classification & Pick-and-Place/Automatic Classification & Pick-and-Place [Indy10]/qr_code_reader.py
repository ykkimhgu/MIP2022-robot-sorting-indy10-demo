import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

part = str(0)

# 로봇(Indy10)과 연동 유무 (0: 연동 x, 1: 연동 o)
robot_subprocess = 1

# 입력값을 보낼 준비 유무 (0: 준비 x, 1: 준비 o)
ready_flag = 0

while(cap.isOpened()):
  # 카메라로 매 프레임마다 이미지를 읽음
  ret, img = cap.read() 

  if not ret:
    continue
  
  # 이미지를 Gray scale로 변환
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
  # Gray scale로 변환된 QR 이미지를 해독
  decoded = pyzbar.decode(gray)
  
  # 2차원 리스트를 선언
  rows = 4  # 부품 개수
  cols = 2  # 부품 순서, 정보 
  qr_list = [[0 for j in range(cols)] for i in range(rows)]

  # QR 개수를 카운트
  cnt = 0

  for d in decoded:
    # QR 코드의 영역을 추출
    x, y, w, h = d.rect

    # QR 코드의 타입과 데이터를 읽음
    barcode_data = d.data.decode("utf-8")
    barcode_type = d.type

    # QR 코드의 데이터를 part에 저장
    part = barcode_data
    center_point_x = x + (w / 2)
    center_point_y = y + (h / 2)

    qr_list[cnt][0] = center_point_x
    qr_list[cnt][1] = barcode_data

    # QR 코드 부분에 사각형을 그림
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # QR 코드의 타입과 데이터를 text에 저장한 뒤에 화면에 나타냄
    text = '%s (%.f, %.f)' % (barcode_data, center_point_x, center_point_y)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    
    # QR 갯수를 업데이트
    cnt += 1

  # 카메라로 매 프레임마다 읽고 있는 이미지를 'img' 윈도우로 보여줌
  cv2.imshow('img', img)
  
  # QR 입력값을 선언
  qr_val = str(0)
  
  # QR 4개가 읽힌 경우 입력값을 정리
  if cnt == 4:
    qr_list.sort()
    ready_flag = 1
    for i in range(0, len(qr_list)):
        if i == 0:
            qr_val = str(qr_list[i][1])
        else:
            qr_val = qr_val + str(qr_list[i][1])
  
  # 로봇과 연동된 상태에서 입력값을 보낼 준비가 되면 반복문에서 나감
  if ready_flag == 1 and robot_subprocess == 1:
    qr_val = qr_val + 'Move'
    ready_flag = 0
    break

  # 'q'를 누르게 되면 location에 종료 구문이 저장된 채로 반복문에서 나감
  key = cv2.waitKey(1)
  if key == ord('q'):
    qr_val = 'StopStopStop'
    break
  # 'p'를 누르게 되면 연습 구문을 저장된 채로 반복문에서 나감
  elif key == ord('p'):
    qr_val = 'A1A2B1B2Move'
    break

# 저장된 QR 입력값을 print하여 qr_classify_robot.py에서 QR 입력값을 읽을 수 있도록 함
print(qr_val)

# 설정해놓은 카메라와 윈도우를 해제
cap.release()
cv2.destroyAllWindows()
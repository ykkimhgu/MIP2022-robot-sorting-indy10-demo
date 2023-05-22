import cv2
import numpy as np
import pyrealsense2 as rs

# Depth Camera 세팅
pipe = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

profile = pipe.start(config)

# Window에 출력되는 text 형식 선언
font                   = cv2.FONT_HERSHEY_SIMPLEX
fontScale              = 1
fontColor              = (0,0,255)
lineType               = 2

# 로봇(Indy10)과 연동 유무 (0: 연동 x, 1: 연동 o)
robot_subprocess = 0

try:
  while True:
    # Depth Camera로 부터 frame을 받으며, Color frame과 Depth frame을 저장
    frameset = pipe.wait_for_frames()
    color_frame = frameset.get_color_frame()
    depth_frame = frameset.get_depth_frame()

    # Color frame의 data를 color에 저장, res에 color를 복사
    color = np.asanyarray(color_frame.get_data())
    res = color.copy()
    
    # color를 GaussianBlur 처리한 뒤 hsv로 변환
    blur_color = cv2.GaussianBlur(color, (5, 5), 0)
    hsv = cv2.cvtColor(blur_color, cv2.COLOR_BGR2HSV)

    # 탐지하고자 하는 색깔의 범위를 설정 (BGR이 아닌 HSV로 설정)
    lower_b = np.array([-10,50,130])
    upper_b = np.array([50,150,230])

    # mask에 탐지된 부분을 띄우며, color에 해당된 부분만 보이게 이미지를 합성
    mask = cv2.inRange(hsv, lower_b, upper_b)
    result = cv2.bitwise_and(color, color, mask=mask)

    # Depth frame에서 depth에 대한 color data를 받음
    colorizer = rs.colorizer()
    colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())

    # Depth 이미지를 맞추기 위한 align 생성
    align = rs.align(rs.stream.color)
    frameset = align.process(frameset)

    # Color frame과 Depth frame을 업데이트
    aligned_depth_frame = frameset.get_depth_frame()
    colorized_depth = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())

    # 업데이트된 Depth frame에서 정보를 받음
    depth_info = aligned_depth_frame.as_depth_frame()

    # mask에서 Contour를 특정
    (c, _) = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # 표면 감지 Flag (0 = 표면 감지 x / 1 = 표면 감지 o)
    surface_on = 0

    for contour in c:

        # 픽셀 거리 측정에 필요한 변수를 선언
        distance_data = 0
        distance_sum = 0
        distance_temp = 0
        pix_cnt = 0

        # 특정 면적 이상의 Contour에 대해서만 진행 (조건: 면적 10000 초과)
        if cv2.contourArea(contour) > 10000:

            # Contour의 최소 면적을 나타내는 사각형을 res에 출력 (회전)
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(res, [box], -1, (255, 0, 0), 3)    

            # 픽셀 범위의 거리 데이터를 기록할 text 파일을 생성
            text = open('Pixel_Area_Distance.txt', 'w')
            
            # Contour와 외접하는 사각형의 정보를 얻음
            (x, y, w, h) = cv2.boundingRect(contour)
            text1_point = (x, y)
            text2_point = (x, y+np.int0(1.2*h))

            # boundingRect의 범위가 640x480 frame의 경계값과 같은 경우 오류가 발생
            if x + w == 640:
                w = w - 1
            if y + h == 480:
                h = h - 1

            # 정해진 픽셀 범위 내의 거리를 측정한 뒤 축적
            for i in range(0, w+1) :
                for j in range(0, h+1) :
                    # 해당 픽셀의 거리 측정 (단위: [cm])
                    distance_data = round((depth_info.get_distance(x+i, y+j) * 100), 2)
                    # 생성된 파일에 픽셀 거리 데이터를 기록
                    data = ('%.f\n' % distance_data)
                    text.write(data)
                    # 적정 거리 내의 픽셀에 대해서만 진행
                    if distance_data > 0 and distance_data <= 60 :
                        res[y+j][x+i] = np.array([255, 255, 255])
                        # 이상치가 제거된 거리 데이터를 축적
                        if pix_cnt == 0 :
                            # 첫번째 픽셀의 거리 데이터를 따로 변수에 저장 및 축적
                            distance_temp = distance_data
                            distance_sum = distance_data
                            pix_cnt = 1
                        elif pix_cnt >= 1 :
                            # 다음 픽셀의 거리 데이터는 비교를 통해 조건 충족 시 저장 및 축적
                            if distance_temp == 0 :
                                distance_temp = 1
                            if (abs(distance_data-distance_temp)/distance_temp) <= 0.2 :
                                # 축적 조건 : 20% 이내의 데이터 
                                distance_sum = distance_sum + distance_data
                                pix_cnt = pix_cnt + 1
                        surface_on = 1
            
            # 생성된 파일을 닫음
            text.close()
        
            # 축적된 거리 값과 사용된 픽셀 수를 통해 평균값을 산출
            if surface_on == 1 :
                dist = distance_sum / pix_cnt

            # Contour에 외접하는 사각형을 res에 출력
            cv2.rectangle(res, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 표면 감시 Flag에 값에 따라 res에 출력되는 text 구분
            if surface_on == 1 :
                text1 = "Depth: " + str("{0:.2f}").format(dist) + "[cm]"
                if robot_subprocess == 0 :
                    surface_on = 0
            elif surface_on == 0 :
                text1 = "Surface distance is not detected well"
            
            # res에 출력되는 text1 형식
            cv2.putText(res,
                        text1,
                        text1_point,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            
            ####### 각도 부분은 추후 디벨롭이 필요함 #######
            # 표면의 각도를 측정 (0 ~ 89도)
            angle = np.int0(round(rect[2], 2))
            
            if angle == 90 :
                angle = 0

            # 표면의 각도를 text로 설정
            text2 = "Angle: " + str("{0:0d}").format(angle) + "[degree]"

            # res에 출력되는 text2 형식
            cv2.putText(res,
                        text2,
                        text2_point,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            
            # 로봇과 연동된 경우 표면을 확인하면 동작 신호 입력
            if surface_on == 1 and robot_subprocess == 1:
                print("Move %d" % angle)
                break

    # 각 Window를 선언한 뒤 출력
    cv2.namedWindow('RBG', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RBG', res)
    cv2.namedWindow('Depth', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Depth', colorized_depth)
    cv2.namedWindow('mask', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('mask', mask)
    cv2.namedWindow('result', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('result', result)

    # 로봇의 동작 신호가 입력된 뒤 프로그램을 종료
    if surface_on == 1 and robot_subprocess == 1:
        cv2.destroyAllWindows()
        break

    # 이미지 취득 종료 ( Q 버튼 or ESC 버튼 )
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q') or key == 27:
        cv2.destroyAllWindows()
        print("Stop")
        break
	
finally:
  # 종료
  pipe.stop()

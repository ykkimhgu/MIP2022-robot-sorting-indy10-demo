# Palletizing Demo Tutorial



## Demo Design

**데모 디자인**은 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208728566-7f9051be-7bab-457c-8e88-b0e882b51dc1.png)





## Demo Process

**데모 진행 순서**는 다음과 같습니다.

1. Depth camera를 통해 **적정 거리 안의 상자 표면을 인식**합니다.
2. **상자 표면의 각도를 산출**합니다.
3. 상자 각도를 Indy10에 보내주어 **해당 각도만큼 헤드(6번 조인트)를 돌려 상자를 집게**합니다.
4. **팔레타이징 순서에 맞는 위치로 상자를 적재**합니다.

해당 순서를 **플로우차트**로 표현하면 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208728604-2cdfe886-ad6e-498b-8bc3-74d0d0ab36d7.png)



## Configuration Equipment

**데모 구성 장비**는 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208728665-a1eb44f0-1efb-4a65-bb88-42dd07604405.png)



## Package Setting

각 장비에 대한 **패키지**는 다음과 같이 세팅합니다.

![image](https://user-images.githubusercontent.com/84532915/208728701-a3d9d38d-89ba-4c80-8387-5470f24fec6e.png)



## Demo Code

데모 코드는 **총 2개로 구성**되어 있습니다. 하나는 **Depth Camera를 통해 상자를 인식**하는 **box_detecter.py** 이고, 다른 하나는 **앞의 코드를 통해 얻은 데이터를 바탕으로 팔레타이징을 실행**하는 **Palletizing_Indy10.py** 입니다.



각 코드마다 **실행에 필요한 세팅**은 다음과 같습니다.

### 1) box_detecter.py

```python
# 로봇(Indy10)과 연동 유무 (0: 연동 x, 1: 연동 o)
robot_subprocess = 0
```

**Indy10과 연동할 경우**에는 **1**로, **아닌 경우**에는 **0**으로 세팅합니다. 이처럼 구분한 이유는 **Indy10과 연동하기 전 Depth Camera만 실행시켜 상자를 잘 인식하며 거리 및 각도를 정확히 산출하는지 확인**하기 위해서입니다.

```python
# 탐지하고자 하는 색깔의 범위를 설정 (BGR이 아닌 HSV로 설정)
lower_b = np.array([-10,50,130])
upper_b = np.array([50,150,230])
```

**Color Detection에서 탐지하고자 하는 색의 경계를 정하는 과정**입니다. 현재 세팅은 **우체국 상자의 색**으로 되어있습니다. 만약 새로운 환경에서 잘 탐지되지 않는다면 **새롭게 사진을 찍은 뒤 BGR 값을 파악한 뒤 해당 값을 HSV 값으로 변환**하여 **기준값을 정한 뒤 적절한 범위를 주어 적용**해주면 되겠습니다. 

```python
# 특정 면적 이상의 Contour에 대해서만 진행 (조건: 면적 10000 초과)
if cv2.contourArea(contour) > 10000:
```

**Color Detection을 통해 탐지된 색에 대한 contour를 선별하는 과정**에서 **기준 면적을 정하는 과정**입니다. 이 값 또한 새로운 환경에서 본인이 판단하여 **필요시 적절한 값으로 바꾸어 적용**해주면 되겠습니다.

```python
# 적정 거리 내의 픽셀에 대해서만 진행
if distance_data > 0 and distance_data <= 60 :
```

**선별된 contour의 모든 픽셀에 대한 거리 데이터를 확인하는 과정**입니다. 이 조건문은 **60 cm 이내의 거리의 픽셀에 대해서만 진행**한다는 의미입니다. 즉, 상자가 60 cm 보다 먼 경우에는 표면이 인식되지 않을겁니다. 그러므로 **상자가 놓여지는 높이 및 카메라 설치 높이에 따라 적절한 값을 적용**해주면 되겠습니다.

```python
if (abs(distance_data-distance_temp)/distance_temp) <= 0.2 :
# 축적 조건 : 20% 이내의 데이터
```

픽셀의 거리 데이터를 축적하는 과정에서 **이상치를 제거하기 위한 과정**입니다. 이 조건은 **기준값으로부터 +- 20% 이내의 데이터만 축적**한다는 의미입니다. 만약 상자의 거리가 오차가 크게 측정된다면 **해당 조건문을 적절한 값으로 수정해보는 것을 추천**합니다.



### 2) Palletizing_Indy10.py

```python
# 1단계: 상자가 놓여지는 고정된 위치의 위로 이동
t_pos = [0.09766, -0.49899, 0.62613, 179.88, 1.51, 96.72]
```

데모 실행에 있어서 **총 2곳의 좌표를 설정**할 필요가 있습니다. 그 중 첫번째 좌표인 **상자가 놓여지는 고정된 위치의 절대 좌표를 입력**해주면 됩니다. (**툴 좌표계로 입력**)

![image](https://user-images.githubusercontent.com/84532915/208728763-4f950eb9-1f55-4d60-83df-675aa14854c3.png)

툴 좌표계는 **Conty의 좌측 상단의 툴 위치**를 통해 확인할 수 있습니다. 
[ **주의: x, y, z 좌표의 경우에는 단위를 mm 가 아닌 m 단위로 입력해야 합니다.** ]

```python
# 최초의 Palletizing 좌표를 설정
# 다음 순서의 Palletizing 좌표는 next_pos_cal() 함수를 통해 계산
if layer == 1 and seq == 1:
	locate_pos = [0.71925, 0.17725, 0.22942, 0.75, 176.55, 5.62]
```

두번째 좌표는 **팔레타이징이 시작되는 곳의 좌표**입니다. 해당 좌표도 마찬가지로 **시작되는 곳의 절대 좌표를 입력**해주면 됩니다. (**툴 좌표계로 입력**)

```python
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
```

해당 함수는 **팔레타이징 순서에 따라 적정한 위치를 계산해주는 함수**입니다. **우체국 상자의 규격에 따라 적절한 값을 입력**해주면 되지만 **규격과 동일한 값을 주게 되면 Indy10의 관절 오류로 인해 상자가 원하는 위치에 놓여지지 않고 오차가 있는 상태로 도달**하게 되어 문제가 발생합니다. 그러므로 이 경우에는 **여러번 시도를 통해 최대한 여유 있는 값을 입력**해주길 바랍니다.
[ **주의: Indy10의 관절 오류는 많은 시도를 해보았지만 불규칙적인 패턴을 보이고 있어서 개선을 위한 연구가 필요해보입니다.** ]



모든 준비가 끝난 경우에는 **box_detecter.py의 robot_subprocess 값을 1로 세팅**한 뒤에 **Palletizing_Indy10.py를 실행**해주면 됩니다.



## Demo Video

**데모 영상**은 유튜브 링크를 통해 확인할 수 있습니다.

* [팔레타이징 데모 영상](https://www.youtube.com/watch?v=YMPplXEOtlA)

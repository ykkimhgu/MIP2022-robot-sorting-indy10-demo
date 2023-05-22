# Automatic Classification & Pick-and-Place Demo Tutorial



## Demo Design

**데모 디자인**은 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208834884-ec7dfd46-7d21-4753-89ef-747e51946737.png)



## Demo Process

**데모 진행 순서**는 다음과 같습니다.

1. PC Camera를 통해 컨베이어 벨트 위에 배치되어 있는 **4개의 상자의 QR code를 인식**합니다.
2. QR code의 data를 바탕으로 Indy10(또는 UR5e)은 **각 상자를 종류에 따라 분류**합니다.
3. 파이썬 함수를 통해 **랜덤으로 상자 배치 순서를 생성**합니다.
4. 생성된 배치 순서에 맞게 Indy10(또는 UR5e)은 **상자를 컨베이어 벨트 위에 재배치**합니다.
5. 재배치된 4개의 상자를 **컨베이어 벨트를 통해 반대편으로 이송**합니다. 

해당 순서를 **플로우차트**로 표현하면 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208834913-00f0f69f-bba4-4cbc-9174-bdee637ff9e6.png)



## Configuration Equipment

**데모 구성 장비**는 다음과 같습니다.

![image](https://user-images.githubusercontent.com/84532915/208834951-116668ce-15ba-43d7-97c1-cd683726738d.png)

![image](https://user-images.githubusercontent.com/84532915/208834977-c3695966-b658-4e7c-a9a1-a990a97cd00e.png)



## Package Setting

각 장비에 대한 **패키지**는 다음과 같이 세팅합니다.

![image](https://user-images.githubusercontent.com/84532915/208835005-aebf929e-b4a7-489c-b326-913fd5ec25a9.png)



## Conveyor Belt

**컨베이어 벨트**는 다음과  같이 세팅합니다.

![circuit (1)](https://user-images.githubusercontent.com/84532915/209643318-b4877d39-2045-49fb-9456-0a5389bfdcb0.png)

세팅이 끝난 뒤에는 **파워 서플라이에 전압은 30V 이상, 전류는 1A 이상**으로 맞춰준 뒤 출력해주면 컨베이어 벨트는 정상적으로 작동할 겁니다. 아래의 사진은 실제로 컨베이어 벨트를 작동시킬 때의 파워 서플라이 상태입니다.

![image](https://user-images.githubusercontent.com/84532915/209468944-2c5c9453-4f90-402b-874a-75a79960d8ec.png)



## Demo Code

데모 코드는 **총 3개로 구성**되어 있습니다. 첫번째는 **PC Camera를 통해 상자의 QR code를 인식**하는 **qr_code_reader.py** 이고, 두번째는 **앞의 코드를 통해 얻은 데이터를 바탕으로 자동 분류 및 픽앤플레이스를 실행**하는 **Automatic_Classification&PickandPlace_Indy10.py** 이고, 마지막은 **파이썬 코드에서 시리얼 통신을 통해 컨베이어 벨트를 원격으로 제어**하게 해주는 **ArduinoUno_ConveyorBelt.ino** 입니다.



각 코드마다 **실행에 필요한 세팅**은 다음과 같습니다.

### 1) qr_code_reader.py

```python
# 로봇(Indy10)과 연동 유무 (0: 연동 x, 1: 연동 o)
robot_subprocess = 1
```

**Indy10과 연동할 경우**에는 **1**로, **아닌 경우**에는 **0**으로 세팅합니다. 이처럼 구분한 이유는 **Indy10과 연동하기 전 PC Camera만 실행시켜 QR code를 잘 인식하며 데이터 및 중심 좌표를 정확히 읽어내는지 확인**하기 위해서입니다.

```python
# 'p'를 누르게 되면 연습 구문을 저장된 채로 반복문에서 나감
elif key == ord('p'):
  qr_val = 'A1A2B1B2Move'
  break
```

해당 구문은 **'p'를 눌렀을 때 'A1A2B1B2Move'라는 명령을 qr_val이라는 명령 전달 변수에 저장**시키라는 의미입니다. 이 구문을 만든 이유는 카메라 성능이 좋지 않아 QR code 인식을 잘 하지 못하고 있는 경우에 **자체적으로 명령을 보내 데모 연습을 진행**하기 위해서입니다. 다양한 조건의 연습을 하고 싶은 경우에 **Move를 제외한 부분을 랜덤으로 조합해 진행**해주시면 되겠습니다.



### 2) Automatic_Classification&PickandPlace_Indy10.py

```python
# Arduino Uno 세팅
py_serial = serial.Serial(
    
    # Windows 포트
    port='COM4',
    
    # 보드 레이트 (통신 속도)
    baudrate=9600,
)
```

**Arduino Uno 보드를 노트북과 연결**할 때 필요한 세팅입니다. 현재 포트는 **COM4**로 세팅되어 있습니다. 하지만 포트는 노트북마다 세팅이 달라질 수 있으므로 **Arduino 실행 화면의 툴에서 본인의 포트에 맞게 수정해서 적용**해주시면 되겠습니다.

![image](https://user-images.githubusercontent.com/84532915/208835102-9a58895b-a42d-446c-b7aa-952b7c3d55dc.png)

```python
# 시작 위치를 설정
start_pos = [0.75474, 0.00010, 0.60269, 179.97, 1.18, 179.92]
```

데모 실행에 있어서 **총 1곳의 좌표를 설정**할 필요가 있습니다. 해당 좌표는 **Indy10을 기준으로 가장 멀리 떨어져있는 상자의 위치**입니다. 해당 위치의 **절대 좌표를 입력**해주면 됩니다.
[ **절대 좌표 관련 설명은 팔레타이징 튜토리얼을 참고** ]

![image](https://user-images.githubusercontent.com/84532915/208835127-0c1ddc67-ee47-4741-a0a2-f183efd03029.png)

```python
# 부품 종류에 따라 움직일 방향 및 거리를 알려주는 함수를 선언
def part_direction(part_list):
    side_move = 0
    if part_list[0] == 'A':
        side_move = 0.225
    elif part_list[0] == 'B':
        side_move = -0.235
    return side_move
```

해당 함수는 **상자의 종류에 따라 Indy10이 움직일 방향 및 거리를 알려주는 함수**입니다. 상자의 종류가 **'A'일 경우에는 왼쪽으로 22.5cm**, '**B'일 경우에는 오른쪽으로 23.5cm 이동**한다는 의미입니다. 새롭게 적용되는 환경에서 양쪽의 보관함의 위치가 달라지는 경우 **컨베이어 벨트 위의 보관함으로부터 양쪽 보관함까지의 거리를 줄자 등을 이용하여 측정한 뒤 업데이트**하면 되겠습니다.



### 3) ArduinoUno_ConveyorBelt.ino

```c
const int pwmPin = 4;
const int dirPin = 2;
```

**Arduino Uno 보드에서 핀을 설정하는 과정**입니다. 현재 세팅은 **PWM은 4번 핀**을 **방향은 2번 핀**으로 되어있습니다. 만약 핀을 다르게 하고 싶다면 **선택한 핀 번호를 해당 부분에 업데이트**하면 되겠습니다.

```c
if (Serial.available()){
  cmd = Serial.read();

if(cmd == 'b'){
  Serial.println("Belt: Backward");
  cnt = 1000;
}

for(i=cnt; i>=0; i-=1){
  digitalWrite(pwmPin, 255);
  delay(5);
  digitalWrite(pwmPin, 0); 
  digitalWrite(dirPin, HIGH);  // 역방향    
}
    
}
```

해당 구문은 **시리얼 통신을 통해 'b'라는 명령을 받았을 때 컨베이어 벨트를 역방향으로 5초동안 작동**시키라는 의미입니다. 이 부분에서 만약 보관함이 정확한 위치에 도착하지 않아 수정을 원하신다면 **cnt 값을 수정**하면 되겠습니다. **컨베이어 벨트의 작동 시간은 cnt * delay time[ms] 이므로 시간 단위를 고려하여 판단**해주시면 되겠습니다. 



모든 준비가 끝난 경우에는 **qr_code_reader.py의 robot_subprocess 값을 1로 세팅**하고,  **ArduinoUno_ConveyorBelt.ino를 Arduino Uno 보드에 업로드**한 뒤에 **Automatic_Classification&PickandPlace_Indy10.py를 실행**해주면 됩니다.



## Future Work

본 데모에서는 **RG2 그리퍼의 호환성 문제**로 인해 UR5e를 사용하지 못했습니다. 하지만 WeGo Robotics 및 OnRobot의 개발자들과 지속적인 연락 및 협업을 통해 그리퍼 호환성 문제를 해결한다면 본 데모를 처음 구상했을 때 목표했었던 **Closed Loop Demo를 구현할 수 있을 것으로 예상**됩니다.



## Demo Video

데모 영상은 유튜브 링크를 통해 확인할 수 있습니다.

* [자동 분류 및 픽앤플레이스 데모 영상](https://www.youtube.com/watch?v=3OCl36IBem8)


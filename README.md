# 2022-2 MIP Robot-Sorting Indy10 Demo

스마트팩토리 산업 로봇 소형 박스 분류 자동화 데모  - 로봇:  Indy 10 -  박스 QR 코드 인식 및 분류 자동화 데모



## Introduction

본 repository는 한동대학교 2022년 2학기에 진행된 기전융합종합설계, **Local Industrial Development through Logistics Automation with Robot Manipulator** 에 대한 실행 파일 및 튜토리얼이 포함되어 있습니다.

스마트팩토리의 **물류 자동화 시스템**을 로봇팔을 기반으로 구현 및 검증하여 지역 산업 종사자와 같은 초심자들이 자동화 공정을 적용할 때 참고할 수 있는 **가이드라인을 제공**하는 것이 목적이었습니다. 해당 연구에서 선택한 물류 공정은 **팔레타이징** 공정과 **자동 분류 및 픽앤플레이스** 공정입니다.



## Requirements

로봇팔 모델은 **Neuromeka** 사의 **Indy10**과 **Universal Robot** 사의 **UR5e**를 사용했으며, 초심자들의 편의와 외부 장비와의 연동을 위해 로봇팔 제어는 티치 펜던트와 ROS가 아닌 **Windows 에서 Python code**를 통해 이루어졌습니다.

Windows에서 Python code를 바탕으로 로봇팔을 제어하기 위해서는 각 로봇팔마다 **Python code로부터 명령 전달을 가능하게 해주는 패키지**가 필요합니다. Indy10의 경우에는 **Python IndyDCP**이며, UR5e의 경우에는 **urx**입니다.

팔레타이징 데모와 자동 분류 및 픽앤플레이스 데모에서 각 로봇팔들의 역할은 **픽앤플레이스**입니다. 카메라와 같은 외부 장비로부터 얻은 데이터를 바탕으로 물체를 원하는 위치로 옮기는 것이 로봇팔의 주 목적이기에 로봇팔에 부착되는 그리퍼도 위의 목적과 부합되는 것을 선택했습니다. Indy10에는 **OnRobot 사의 진공 그리퍼인 VGC10**을 사용했으며, UR5e에는 **OnRobot 사의 두 손가락 그리퍼인 RG2**를 사용했습니다.

Python code는 카메라의 영상처리 기법을 바탕으로한 외부 데이터 취득을 위해 **Python 3 버전**을 사용했습니다.



## Contents

본 튜토리얼은 로봇팔 1대와 카메라 1개로 이루어져 상대적으로 구현하기 쉬운 팔레타이징 공정을 먼저 구현한 뒤 검증했습니다. 팔레타이징 공정이란 **물류 작업 시 출하나 보관을 위해 물품을 팔레트(화물 운반대) 위에 적재하는 것**을 의미합니다.

- **[팔레타이징 공정 튜토리얼](https://github.com/Sanghyeon-K/2022-2_MCE_Capstone_AutomationSystem/blob/main/Palletizing%20%5BIndy10%5D/Palletizing%20Demo%20Tutorial.md)**

  

팔레타이징 공정을 성공적으로 구현한 뒤에는 카메라와 컨베이어 벨트를 포함해 보다 많은 외부 장비를 사용하는 자동 분류 및 픽앤플레이스 공정을 구현한 뒤 검증했습니다. 자동 분류 및 픽앤플레이스 공정이란 **사용자가 설정한 조건에 따라 물품을 구분한 뒤 각 물품마다 해당되는 장소로 옮기는 것**을 의미합니다. 

* **[자동 분류 및 픽앤플레이스 공정 튜토리얼](https://github.com/Sanghyeon-K/2022-2_MCE_Capstone_AutomationSystem/blob/main/Automatic%20Classification%20%26%20Pick-and-Place/Automatic%20Classification%20%26%20Pick-and-Place%20Demo%20Tutorial.md)**

  

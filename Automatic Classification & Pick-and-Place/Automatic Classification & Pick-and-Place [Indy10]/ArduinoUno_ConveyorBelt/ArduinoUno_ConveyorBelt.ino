//const int pwmPin = 11;
//const int dirPin = 2;
//
//char cmd;
//
//void setup(){
//  Serial.begin(9600);             // 시리얼 통신 시작(Boadrate : 9600)
//  pinMode(dirPin, OUTPUT);
//  pinMode(pwmPin, OUTPUT);
//}

//void loop(){
//
//  if (Serial.available()){
//    cmd = Serial.read();
//
//    if(cmd == 'f'){
//      Serial.println("Belt: Foward");
//      analogWrite(pwmPin, 127);   // 컨베이어 동작 시작
//      digitalWrite(dirPin, LOW);  // 정방향
//      delay(5000);
//      analogWrite(pwmPin, 0);     // 컨베이어 동작 중지
//    }
//    else if(cmd == 'b'){
//      Serial.println("Belt: Backward");
//      analogWrite(pwmPin, 127);   // 컨베이어 동작 시작
//      digitalWrite(dirPin, HIGH); // 역방향
//      delay(5000);
//      analogWrite(pwmPin, 0);     // 컨베이어 동작 중지
//    }
//  }
//}

//const int pwmPin = 11;
const int pwmPin = 4;
const int dirPin = 2;

char cmd;
int i=0;
int cnt = 0;
int stop_flag = 0;

void setup(){
  Serial.begin(9600);            // 시리얼 통신 시작(Boadrate : 9600)
  pinMode(dirPin, OUTPUT);
  pinMode(pwmPin, OUTPUT);
}

void loop(){

  if (Serial.available()){
    cmd = Serial.read();

  if(cmd == 'f'){
    Serial.println("Belt: Forward");
    digitalWrite(dirPin, LOW);  // 정방향  
    cnt = 1000;
  }

  if(cmd == 'b'){
    Serial.println("Belt: Backward");
    digitalWrite(dirPin, HIGH);  // 역방향  
    cnt = 1000;
  }

  for(i=cnt; i>=0; i-=1){
    digitalWrite(pwmPin, 255);
    delay(5);
    digitalWrite(pwmPin, 0); 
  }
}
}

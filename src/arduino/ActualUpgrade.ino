#include "SerialTransfer.h"
SerialTransfer myTransfer;
float action[3]; //an array to store incoming data from python

#define PI 3.1415926535897932384626433832795


float tim;
float t;
float Bx;
float By;
float Bz;
float gamma;
float omega;
float rolling_frequency;
float alpha;
float amplitude;

//Coil 1 : +Y
const int Coil1_PWMR = 2;
const int Coil1_PWML = 3;
const int Coil1_ENR = 28;
const int Coil1_ENL = 29;

//Coil 2 : +X
const int Coil2_PWMR = 4;
const int Coil2_PWML = 5;
const int Coil2_ENR = 30;
const int Coil2_ENL = 31;

//Coil 3 : -Y
const int Coil3_PWMR = 6;
const int Coil3_PWML = 7;
const int Coil3_ENR = 32;
const int Coil3_ENL = 33;

//Coil 4: -X
const int Coil4_PWMR = 8;
const int Coil4_PWML = 9;
const int Coil4_ENR = 22;
const int Coil4_ENL = 23;

//Coil 5 : +Z
const int Coil5_PWMR = 10;
const int Coil5_PWML = 11;
const int Coil5_ENR = 24;
const int Coil5_ENL = 25;

//Coil 6 : -Z
const int Coil6_PWMR = 12;
const int Coil6_PWML = 13;
const int Coil6_ENR = 26;
const int Coil6_ENL = 27;



  
void setup()
{
  cli();
  TCCR0B = (TCCR0B & 0b11111000) | 0x01; //62.5 [kHz] pin 13,4
  TCCR1B = (TCCR1B & 0b11111000) | 0x01; //31.37255 [kHz] pin 12,11
  TCCR2B = (TCCR2B & 0b11111000) | 0x01; //31.37255 [kHz] pin 10,9
  TCCR3B = (TCCR3B & 0b11111000) | 0x01; //31.37255 [kHz] pin 5,3,2
  TCCR4B = (TCCR4B & 0b11111000) | 0x01; //31.37255 [kHz] pin 8,7,6 

  sei();
  Serial.begin(2000000);
  myTransfer.begin(Serial);
  
 

  

  //Coil1 Ouptut
  pinMode(Coil1_PWMR, OUTPUT);  
  pinMode(Coil1_PWML, OUTPUT);
  pinMode(Coil1_ENR, OUTPUT);  
  pinMode(Coil1_ENL, OUTPUT); 

  //Coil2 Output
  pinMode(Coil2_PWMR, OUTPUT);  
  pinMode(Coil2_PWML, OUTPUT);
  pinMode(Coil2_ENR, OUTPUT);  
  pinMode(Coil2_ENL, OUTPUT); 

  //Coil3 Output
  pinMode(Coil3_PWMR, OUTPUT);  
  pinMode(Coil3_PWML, OUTPUT);
  pinMode(Coil3_ENR, OUTPUT);  
  pinMode(Coil3_ENL, OUTPUT); 

  //Coil4 Output
  pinMode(Coil4_PWMR, OUTPUT);  
  pinMode(Coil4_PWML, OUTPUT);
  pinMode(Coil4_ENR, OUTPUT);  
  pinMode(Coil4_ENL, OUTPUT); 

  //Coil5 Output
  pinMode(Coil5_PWMR, OUTPUT);  
  pinMode(Coil5_PWML, OUTPUT);
  pinMode(Coil5_ENR, OUTPUT);  
  pinMode(Coil5_ENL, OUTPUT);

  //Coil6 Output
  pinMode(Coil6_PWMR, OUTPUT);  
  pinMode(Coil6_PWML, OUTPUT);
  pinMode(Coil6_ENR, OUTPUT);  
  pinMode(Coil6_ENL, OUTPUT);

}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set1(float DC1){
  
  digitalWrite(Coil1_ENR,HIGH);
  digitalWrite(Coil1_ENL,HIGH);
  if (DC1 > 0){
    analogWrite(Coil1_PWMR,abs(DC1)*255);
    analogWrite(Coil1_PWML,0);
  }
  else if (DC1 <= 0){
    analogWrite(Coil1_PWMR,0);
    analogWrite(Coil1_PWML,abs(DC1)*255);
  }
  //Serial.print(DC1);
  //Serial.print(" ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set2(float DC2){
  digitalWrite(Coil2_ENR,HIGH);
  digitalWrite(Coil2_ENL,HIGH);
  if (DC2 > 0){
    analogWrite(Coil2_PWMR,abs(DC2)*255);
    analogWrite(Coil2_PWML,0);
  }
  else if (DC2 < 0){
    analogWrite(Coil2_PWMR,0);
    analogWrite(Coil2_PWML,abs(DC2)*255);
  }
  //Serial.print(DC2);
  //Serial.print(" ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set3(float DC3){
  digitalWrite(Coil3_ENR,HIGH);
  digitalWrite(Coil3_ENL,HIGH);
  if (DC3 > 0){
    analogWrite(Coil3_PWMR,abs(DC3)*255);
    analogWrite(Coil3_PWML,0);
  }
  else if (DC3 < 0){
    analogWrite(Coil3_PWMR,0);
    analogWrite(Coil3_PWML,abs(DC3)*255);
  }
  //Serial.print(DC3);
  //Serial.print(" ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set4(float DC4){
  digitalWrite(Coil4_ENR,HIGH);
  digitalWrite(Coil4_ENL,HIGH);
  if (DC4 > 0){
    analogWrite(Coil4_PWMR,abs(DC4)*255);
    analogWrite(Coil4_PWML,0);
  }
  else if (DC4 < 0){
    analogWrite(Coil4_PWMR,0);
    analogWrite(Coil4_PWML,abs(DC4)*255);
  }
  //Serial.print(DC4);
  //Serial.print(" ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set5(float DC5){
  digitalWrite(Coil5_ENR,HIGH);
  digitalWrite(Coil5_ENL,HIGH);
  if (DC5 > 0){
    analogWrite(Coil5_PWMR,abs(DC5)*255);
    analogWrite(Coil5_PWML,0);
  }
  else if (DC5 < 0){
    analogWrite(Coil5_PWMR,0);
    analogWrite(Coil5_PWML,abs(DC5)*255);
  }
  //Serial.print(DC5);
  //Serial.print(" ");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void set6(float DC6){
  digitalWrite(Coil6_ENR,HIGH);
  digitalWrite(Coil6_ENL,HIGH);
  if (DC6 > 0){
    analogWrite(Coil6_PWMR,abs(DC6)*255);
    analogWrite(Coil6_PWML,0);
  }
  else if (DC6 < 0){
    analogWrite(Coil6_PWMR,0);
    analogWrite(Coil6_PWML,abs(DC6)*255);
  }
  //Serial.println(DC6);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



void loop()
{
  
    if  (myTransfer.available()){
      
              uint16_t message = 0;
              message = myTransfer.rxObj(action,message);
    
    }
    
    
  if (action[0] == 1){ // ROLL
       
       alpha = action[1];
       rolling_frequency = action[2]; 
       omega = 2*PI*rolling_frequency;
       gamma = 90;
       tim = micros() % 62500000;
       t = tim / 62500000;
       
       Bx = cos(gamma)*cos(alpha)*cos(omega*t) + sin(alpha)*sin(omega*t);
       By = -cos(gamma)*sin(alpha)*cos(omega*t) + cos(alpha)*sin(omega*t); 
       Bz = sin(gamma)*cos(omega*t);

       set1(By);
       set2(Bx);
       set3(-By);
       set4(-Bx);
       set5(Bz);
       set6(-Bz);
     
    }
    else if (action[0] == 2){  //ORIENT
      
      alpha = action[1];
      amplitude = action[2];
      Bx = amplitude*cos(alpha);
      By = amplitude*sin(alpha);
      Bz = 0;
      set1(By);
      set2(Bx);
      set3(-By);
      set4(-Bx);
      set5(Bz);
      set6(-Bz);
    }
    else if (action[0] == 4){  //OFF
     
       digitalWrite(Coil1_ENR,LOW);
       digitalWrite(Coil1_ENL,LOW);
       digitalWrite(Coil2_ENR,LOW);
       digitalWrite(Coil2_ENL,LOW);
       digitalWrite(Coil3_ENR,LOW);
       digitalWrite(Coil3_ENL,LOW);
       digitalWrite(Coil4_ENR,LOW);
       digitalWrite(Coil4_ENL,LOW);
       digitalWrite(Coil5_ENR,LOW);
       digitalWrite(Coil5_ENL,LOW);
       digitalWrite(Coil6_ENR,LOW);
       digitalWrite(Coil6_ENL,LOW);
    }
    
    
      
  }    

  
  

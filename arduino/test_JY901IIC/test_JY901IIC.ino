#include <Wire.h>
#include <JY901.h>
/*
Test on Uno R3.
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/
void setup() 
{
  Serial.begin(9600);
  JY901.StartIIC();
} 

void loop() 
{
  //print received data. Data was received in serialEvent;
 JY901.GetAngle();
 Serial.println((float)JY901.stcAngle.Angle[2]/32768*180);
 

  delay(10);
}




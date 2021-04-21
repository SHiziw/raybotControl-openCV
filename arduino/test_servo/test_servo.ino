#include <Wire.h>
#include <JY901.h>
#include <Servo.h>
/*
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/

Servo leftServo;  // create servo object to control a servo
Servo rightServo; // create servo object to control a servo
// twelve servo objects can be created on most boards
int leftPos = 0;                     // variable to store the left servo position, expressed by microseconds. 
int rightPos = 0;                     // variable to store the rihgt servo position, expressed by microseconds. 
float leftFreq = 0.0;                   //angular velocity, Hz
float rightFreq = 0.0;
unsigned long l_previousMillis = 0; 
unsigned long r_previousMillis = 0; 
unsigned long now = 0;
unsigned long servoDelay = 5;
int pos =1500;
void setup()
{
  //Serial.begin(9600);
  //JY901.StartIIC();
  leftServo.attach(9);   // attaches the servo on pin D9 to the left servo object
  rightServo.attach(10); // attaches the servo on pin D10 to the right servo object
}

void loop()
{
  //print received data. Data was received in serialEvent;
  /*
  leftServo.writeMicroseconds(pos);  // tell servo to go to position in variable 'pos'
  rightServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
  delay(1000);
  */
  now = millis();
  if (now - l_previousMillis >= servoDelay)
  {
    l_previousMillis = millis();
    leftPos = (int)300 * sin(6.2821853 * leftFreq * now / 1000) + 1800;
    leftServo.writeMicroseconds(leftPos); // tell servo to go to position in variable 'pos'
  }
  now = millis();
  if (now - r_previousMillis >= servoDelay)
  {
    r_previousMillis = millis();
    rightPos = (int)-300 * sin(6.2821853 * rightFreq * now / 1000) + 1200;
    rightServo.writeMicroseconds(rightPos); // tell servo to go to position in variable 'pos'
  }
}

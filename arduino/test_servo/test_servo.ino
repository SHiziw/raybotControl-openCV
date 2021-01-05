#include <Wire.h>
#include <JY901.h>
#include <Servo.h>
/*
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/

Servo leftServo; // create servo object to control a servo
Servo rightServo; // create servo object to control a servo
// twelve servo objects can be created on most boards
int pos = 0; // variable to store the servo position
void setup()
{
  Serial.begin(9600);
  JY901.StartIIC();
  leftServo.attach(5); // attaches the servo on pin D5 to the left servo object
  rightServo.attach(6); // attaches the servo on pin D6 to the right servo object
}

void loop()
{
  //print received data. Data was received in serialEvent;
  JY901.GetAngle();
  Serial.println((float)JY901.stcAngle.Angle[2] / 32768 * 180);

  for (pos = 900; pos <= 2100; pos += 10)
  { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    leftServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
    rightServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
    delay(10);          // waits 15ms for the servo to reach the position
  }
  for (pos = 2100; pos >= 900; pos -= 10)
  {                     // goes from 180 degrees to 0 degrees
    leftServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
    rightServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
    delay(10);          // waits 15ms for the servo to reach the position
  }
}

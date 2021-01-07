#include <Wire.h>
#include <JY901.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <PID_v1.h>
/*
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/
//Define Variables we'll be connecting to
double Setpoint, Input, Output;
double kp, ki, kd;

//Specify the links and initial tuning parameters
PID und_PID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);

Servo leftServo;  // create servo object to control a servo
Servo rightServo; // create servo object to control a servo
// twelve servo objects can be created on most boards
int pos = 0;                     // variable to store the servo position
SoftwareSerial LFCserial(9, 10); //定义虚拟串口名为LFCserial,rx为9号端口,tx为10号端口
char command;

void handleSpeed(double command)
{

}

void handleCommand(uint8_t command)
{
    //und_PID.SetTunings(kp, ki, kd);
}

void setup()
{
    Serial.begin(9600);
    JY901.StartIIC();
    leftServo.attach(5);   // attaches the servo on pin D5 to the left servo object
    rightServo.attach(6);  // attaches the servo on pin D6 to the right servo object
    LFCserial.begin(9600); //初始化虚拟串口
    Serial.begin(9600);    //初始化Arduino默认串口

    //initialize the variables we're linked to
    Input = 10.0; //todo: setting input.
    Setpoint = 100.0; // todo :setting angle.
    und_PID.SetSampleTime(20);

    //turn the PID on
    und_PID.SetMode(AUTOMATIC);
}

void loop()
{


    //print received data. Data was received in serialEvent;
    JY901.GetAngle();
    double angleZ = (float)JY901.stcAngle.Angle[2] / 32768 * 180;
    Serial.println(angleZ);
    Input = angleZ;
    und_PID.Compute();
    handleSpeed(Output);

    for (pos = 900; pos <= 2100; pos += 10)
    { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        leftServo.writeMicroseconds(pos);  // tell servo to go to position in variable 'pos'
        rightServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
        delay(10);                         // waits 15ms for the servo to reach the position
    }
    for (pos = 2100; pos >= 900; pos -= 10)
    {                                      // goes from 180 degrees to 0 degrees
        leftServo.writeMicroseconds(pos);  // tell servo to go to position in variable 'pos'
        rightServo.writeMicroseconds(pos); // tell servo to go to position in variable 'pos'
        delay(10);                         // waits 15ms for the servo to reach the position
    }

    if (LFCserial.available()) //虚拟串口的用法和默认串口的用法基本一样
    {
        command = LFCserial.read();
        Serial.print(command);
        handleCommand(command);
    }
}

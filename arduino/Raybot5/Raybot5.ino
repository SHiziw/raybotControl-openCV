#include <Wire.h>
#include <JY901.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <PID_v1.h>
#include <EEPROM.h>
/*
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/
//Define Variables we'll be connecting to
double Setpoint, Input, Output;
float kp, ki, kd;
static unsigned char receivedCommand[9];
float *p_encode;

//Specify the links and initial tuning parameters
PID und_PID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);

Servo leftServo;  // create servo object to control a servo
Servo rightServo; // twelve servo objects can be created on most boards
SoftwareSerial LFCserial(9, 10); //定义虚拟串口名为LFCserial,rx为9号端口,tx为10号端口

int leftPos = 0;                     // variable to store the left servo position, expressed by microseconds. 
int rightPos = 0;                     // variable to store the rihgt servo position, expressed by microseconds. 
float leftFreq = 1.0;                   //angular velocity, Hz
float rightFreq = 1.0;
unsigned long l_previousMillis = 0; 
unsigned long r_previousMillis = 0; 
unsigned long now = 0;
unsigned long servoDelay = 10;

void handleSpeed(double command)
{
}

void handleCommand()
{
    Serial.print("get: " + receivedCommand[0]);
    switch (receivedCommand[0])
    {
    case 'p':
    {
        switch (receivedCommand[1])
        {
        case 'p':
        {
            kp = *p_encode; //该指针指向receivedCommand[2]
            und_PID.SetTunings(kp, ki, kd);
            break;
        }
        case 'i':
        {
            ki = *p_encode; //该指针指向receivedCommand[2]
            und_PID.SetTunings(kp, ki, kd);
            break;
        }
        case 'd':
        {
            kd = *p_encode; //该指针指向receivedCommand[2]
            und_PID.SetTunings(kp, ki, kd);
            break;
        }

        default:
        {
            //PID setting error!
            break;
        }
        }
        break;
    }
    default:
    {
        //unkown command.
        break;
    }
    }
}
int PIDreadROM(){
    if (EEPROM.length()<12){
        //TODO:no data for PID!
        return -1;
    }
    EEPROM.get(0, kp);
    EEPROM.get(4, ki);
    EEPROM.get(8, kd);
    return 1;

}
int PIDwriteROM(){
    EEPROM.put(0, kp);
    EEPROM.put(4, ki);
    EEPROM.put(8, kd);
    return 1;
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
    Input = 10.0;     //todo: setting input.
    Setpoint = 100.0; // todo :setting angle.
    //und_PID.SetSampleTime(20);

    //turn the PID on
    und_PID.SetMode(AUTOMATIC);

    p_encode = (float *)(receivedCommand + 2); //将unsigned char类型的指针转化成浮点数类型指针，使得储存的4个字节能解析为浮点数
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

    now = millis();
    if (now-l_previousMillis >= servoDelay){
        l_previousMillis = millis();
        leftPos = (int) 600*sin(6.2821853*leftFreq*now/1000)+1500;
        leftServo.writeMicroseconds(leftPos);  // tell servo to go to position in variable 'pos'
    }
    now = millis();
    if (now-r_previousMillis >= servoDelay){
        r_previousMillis = millis();
        rightPos = (int) 600*sin(6.2821853*rightFreq*now/1000)+1500;
        rightServo.writeMicroseconds(rightPos);  // tell servo to go to position in variable 'pos'
    }
    

    if (LFCserial.available() > 8) //虚拟串口的用法和默认串口的用法基本一样
    {
        static char data, i;
        for (i = 0; i < 9; i++)
        {
            data = LFCserial.read();
            receivedCommand[i] = data;
        }
        handleCommand();
        while (LFCserial.available())
        {
            data = LFCserial.read();
        }
    }
}

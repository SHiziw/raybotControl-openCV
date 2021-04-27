#include <Wire.h>
#include <JY901.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <PID_v2.h>

/*
JY901    UnoR3
SDA <---> SDA
SCL <---> SCL
*/
//Define Variables we'll be connecting to
double Setpoint, Input, Output;
float kp, ki, kd;
static int usePID = 0;
static unsigned char receivedCommand[9];
float f_data;

//Specify the links and initial tuning parameters
PID und_PID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);
Servo leftServo;                // create servo object to control a servo
Servo rightServo;               // twelve servo objects can be created on most boards
SoftwareSerial LFCserial(7, 6); //定义虚拟串口名为LFCserial,rx为7号端口,tx为6号端口

int leftPos = 0;      // variable to store the left servo position, expressed by microseconds.
int rightPos = 0;     // variable to store the rihgt servo position, expressed by microseconds.
float leftFreq = 0.0; // angular velocity, Hz
float rightFreq = 0.0;
float phaseL;
float phaseR;
float finsSup = 2100.0; // 最大上限2100，最小下限900，平衡位置1500
float finsInf = 900.0; // 最大上限2100，最小下限900，平衡位置1500
unsigned long l_previousMillis = 0;
unsigned long r_previousMillis = 0;
unsigned long now = 0;
unsigned long servoDelay = 10;


typedef union  
{  
    float fdata;  
    unsigned long ldata;  
}FloatLongType;  

void Byte_to_Float(float *f,unsigned char byte[])  
{  
    FloatLongType fl;  
    fl.ldata=0;  
    fl.ldata=byte[3];  
    fl.ldata=(fl.ldata<<8)|byte[2];  
    fl.ldata=(fl.ldata<<8)|byte[1];  
    fl.ldata=(fl.ldata<<8)|byte[0];  
    *f=fl.fdata;  
} 

void handleSpeed(double error)
{
}

void handleCommand()
{
    unsigned char b[4]={receivedCommand[2],receivedCommand[3],receivedCommand[4],receivedCommand[5]};
    Byte_to_Float(&f_data,b);
    switch (receivedCommand[0])
    {
    case 'P': //command[0]
    {
        switch (receivedCommand[1])
        {
        case 'P': //command[1]
        {
            kp = f_data; //该指针指向receivedCommand[2]
            und_PID.SetTunings(kp, ki, kd);
            break;
        }
        case 'I': //command[1]
        {
            ki = f_data; //该指针指向receivedCommand[2]
            und_PID.SetTunings(kp, ki, kd);
            break;
        }
        case 'D': //command[1]
        {
            kd = f_data; //该指针指向receivedCommand[2]
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
    case 'M': //command[0]
    {
        switch (receivedCommand[1])
        {
        case 'F': //command[1]
        {
            leftFreq = f_data; //该指针指向receivedCommand[2]
            rightFreq = f_data;
            usePID = 1;
            JY901.GetAngle();
            Setpoint = (float)JY901.stcAngle.Angle[2] / 32768 * 180;
            break;
        }
        case 'R': //command[1]
        {
            //leftFreq = 0;
            rightFreq = f_data;
            break;
        }
        case 'L': //command[1]
        {
            leftFreq = f_data; //该指针指向receivedCommand[2]
            //rightFreq = 0;
            break;
        }
        case 'U': //command[1] 波幅上确界
        {
            finsSup = f_data; //该指针指向receivedCommand[2]
            break;
        }
        case 'D': //command[1] 波幅下确界
        {
            finsInf = f_data; //该指针指向receivedCommand[2]

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
    case 'S':
    { //command[0]
        leftFreq = 0;
        rightFreq = 0;
        usePID = 0;
        leftServo.writeMicroseconds(1500);
        rightServo.writeMicroseconds(1500);
        break;
    }

    default:
    {
        //unkown command.
        leftFreq = 0;
        rightFreq = 0;
        usePID = 0;
        leftServo.writeMicroseconds(1500);
        rightServo.writeMicroseconds(1500);
        break;
    }
    }
}
/** //TODO:XIAO do not have a EEPROM
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
**/
void setup()
{

    JY901.StartIIC();
    leftServo.attach(9);   // attaches the servo on pin D9 to the left servo object
    rightServo.attach(10); // attaches the servo on pin D10 to the right servo object
    LFCserial.begin(9600); //初始化虚拟串口
    //Serial.begin(9600);    //初始化Arduino默认串口
    //initialize the variables we're linked to
    Input = 10.0;     //todo: setting input.
    Setpoint = 100.0; // todo :setting angle.
    //und_PID.SetSampleTime(20);

    //turn the PID on
    und_PID.SetMode(AUTOMATIC);

}

void loop()
{

    /*print received data. Data was received in serialEvent;
    JY901.GetAngle();
    double angleZ = (float)JY901.stcAngle.Angle[2] / 32768 * 180;
    Serial.println(angleZ);
    */

    if (usePID)
    {
        JY901.GetAngle();
        Input = (float)JY901.stcAngle.Angle[2] / 32768 * 180;
        und_PID.Compute();
        handleSpeed(Output);
    }

    now = millis();
    if (now - l_previousMillis >= servoDelay)
    {
        l_previousMillis = millis();
        phaseL += leftFreq * servoDelay / 1000;
        phaseL = phaseL - (int)phaseL;
        leftPos = (int)(finsSup - finsInf) * sin(6.2821853 * phaseL) + 0.5 * (finsSup + finsInf);
        leftServo.writeMicroseconds(leftPos); // tell servo to go to position in variable 'pos'
    }
    now = millis();
    if (now - r_previousMillis >= servoDelay)
    {
        r_previousMillis = millis();
        phaseR += rightFreq * servoDelay / 1000;
        phaseR = phaseR - (int)phaseR;
        rightPos = (int)-(finsSup - finsInf) * sin(6.2821853 * phaseR) + 3000 - 0.5 * (finsSup + finsInf); //平衡位置与左边对称
        rightServo.writeMicroseconds(rightPos);                                                            // tell servo to go to position in variable 'pos'
    }

    if (LFCserial.available()>5) //虚拟串口的用法和默认串口的用法基本一样
    {
        static int i;
        i = LFCserial.readBytesUntil('X',receivedCommand,6);
        if (i=6){
        handleCommand();
        }
        

    }
 delay(5);
}

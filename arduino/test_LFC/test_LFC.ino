#include <SoftwareSerial.h>
SoftwareSerial LFCserial(7, 6); //定义虚拟串口名为LFCserial,rx为7号端口,tx为6号端口
static unsigned char receivedCommand[7];
float *p_encode;

float leftFreq = 0.0; // angular velocity, Hz
float rightFreq = 0.0;
void handleCommand()
{
    Serial.print(char(receivedCommand[0]));
    Serial.print(char(receivedCommand[1]));
    Serial.print(", num: ");
    Serial.println(*p_encode);
    switch (receivedCommand[0])
    {

    case 'M': //command[0]
    {
        switch (receivedCommand[1])
        {
        case 'F': //command[1]
        {
            leftFreq = *p_encode; //该指针指向receivedCommand[2]
            rightFreq = *p_encode;
            break;
        }
        case 'R': //command[1]
        {
            //leftFreq = 0;
            rightFreq = *p_encode;
            break;
        }
        case 'L': //command[1]
        {
            leftFreq = *p_encode; //该指针指向receivedCommand[2]
            //rightFreq = 0;
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
       
        break;
    }

    default:
    {
        //unkown command.
        leftFreq = 0;
        rightFreq = 0;
        
        break;
    }
    }
}

void setup()
{
  LFCserial.begin(9600); //初始化虚拟串口
  Serial.begin(9600); //初始化Arduino默认串口
  p_encode = (float *)(receivedCommand + 2);
}
char a;
void loop()
{
    if (LFCserial.available()>5) //虚拟串口的用法和默认串口的用法基本一样
    {
        Serial.print("ok1");
        static int i;
        i = LFCserial.readBytesUntil('X',receivedCommand,6);
        if (i=6){
        Serial.print("ok2");
        handleCommand();
        }
        

    }
    delay(5);
}
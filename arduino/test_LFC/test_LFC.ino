#include <SoftwareSerial.h>
SoftwareSerial LFCserial(7, 6); //定义虚拟串口名为LFCserial,rx为7号端口,tx为6号端口
static unsigned char receivedCommand[7];
float f_data;

float leftFreq = 0.0; // angular velocity, Hz
float rightFreq = 0.0;



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

void handleCommand()
{
    unsigned char b[4]={receivedCommand[2],receivedCommand[3],receivedCommand[4],receivedCommand[5]};
    Byte_to_Float(&f_data,b);
    
    Serial.print(char(receivedCommand[0]));
    Serial.print(char(receivedCommand[1]));
    Serial.print(", num: ");
    Serial.println(f_data);
    switch (receivedCommand[0])
    {

    case 'M': //command[0]
    {
        switch (receivedCommand[1])
        {
        case 'F': //command[1]
        {
            leftFreq = f_data; //该指针指向receivedCommand[2]
            rightFreq = f_data;
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
            Serial.print("left: ");
            Serial.println(leftFreq);
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
}
char a;
void loop()
{
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
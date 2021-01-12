#include <SoftwareSerial.h>
SoftwareSerial LFCserial(7, 6); //定义虚拟串口名为LFCserial,rx为7号端口,tx为6号端口
void setup()
{
  LFCserial.begin(9600); //初始化虚拟串口
  Serial.begin(9600); //初始化Arduino默认串口
}
char a;
void loop()
{
  if (LFCserial.available()) //虚拟串口的用法和默认串口的用法基本一样
  {
    a = LFCserial.read();
    Serial.print(a);
  }
  /*
  LFCserial.println("123,456");
  delay(1000);
  */
}
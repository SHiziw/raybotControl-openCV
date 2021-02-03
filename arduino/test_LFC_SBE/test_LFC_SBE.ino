#include <SoftwareSerial.h>
SoftwareSerial LFCserial(7, 6); //定义虚拟串口名为LFCserial,rx为7号端口,tx为6号端口
void setup()
{
  LFCserial.begin(9600); //初始化虚拟串口
  //Serial.begin(9600); //初始化Arduino默认串口
  pinMode(LED_BUILTIN, OUTPUT);
}
char a;
void loop()
{
  LFCserial.print("A");
  delay(100);  
  if (LFCserial.available()) //虚拟串口的用法和默认串口的用法基本一样
  {
    while(LFCserial.available()){
      a = LFCserial.read();
      //Serial.println(a);
      }
     digitalWrite(LED_BUILTIN, LOW);   // turn the LED on (HIGH is the voltage level)
      delay(500);  
  }
  digitalWrite(LED_BUILTIN, HIGH);  
  delay(100);  
  /*
  LFCserial.println("123,456");
  delay(1000);
  */
}

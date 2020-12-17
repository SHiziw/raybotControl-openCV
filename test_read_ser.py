import serial
import time

ser = serial.Serial("/dev/ttyAMA0", 9600)


def main():
    while True:
        recv = get_recv()
        if recv != None:
            print(recv)
            ser.write(recv[0] + "\n")
        time.sleep(0.1)
    
            
def get_recv():
    cout = ser.inWaiting()
    if cout != 0:
        line = ser.read(cout)
        recv = str.split(line)
        ser.reset_input_buffer()
        return recv
 
   
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()
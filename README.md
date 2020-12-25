# Function for this platform

## Raybot program on board
- **server.py** 

  > Main program.

  - control command data transmission by:
    - tcp_server(): TCP/IP server 
    - UART(via LFC chip)
  - Visual Servo module
    - zmq server
  - sensor data collector

- MotorDriver.py

- PCA9685.py

- RayPID.py

- RayADRC.py

## Android client

- client_tkinter.py

  > need Pydroid 3 to run.
  
  - UI
  - TCP/IP client (send command)
  - zmq client (receive video stream)
  - UART writer/reader
  
## SBE client

- client_tkinter_SBE.py
- 
  > work as a Low frequency remote control.

  - UI
  - UART writer
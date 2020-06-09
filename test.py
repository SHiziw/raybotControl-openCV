from RayPID import PID
RPID = PID(0.006, 0.001, 0.005)
while 1:
    RPID.update(int(input()))
    print(RPID.output)
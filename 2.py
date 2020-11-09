import time
import csv
from time import sleep

with open("/home/pi/raybotControl/power_{}.csv".format(int(round(time.time()*1000))),"w", newline='') as csvfile: 
    writer = csv.writer(csvfile)
    t=int(round(time.time()*1000))
    k=0
    #先写入columns_name
    writer.writerow([int(round(time.time()*1000))-t,1, 2, 3, 4, '0'])
    while k<10:
        k+=1
        sleep(0.1)
        writer.writerow([int(round(time.time()*1000))-t,1, 2, 3, 4, '0'])
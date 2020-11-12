import time
import csv
from time import sleep

with open("./power_{}.csv".format(int(round(time.time()*1000))),"w", newline='') as csvfile: 
    writer = csv.writer(csvfile)
    t=int(round(time.time()*1000))
    k=0
    #先写入columns_name
    writer.writerow([time.asctime(time.localtime(t/1000)),t])
    writer.writerow(["经过毫秒数","总线电压1", "分压电压1", "功率1", "电流1", "总线电压2", "分压电压2", "功率2", "电流2"])
    writer.writerow([int(round(time.time()*1000))-t,1, 2, 3, 4, '0'])
    while k<10:
        k+=1
        sleep(0.1)
        writer.writerow([int(round(time.time()*1000))-t,1, 2, 3, 4, '0'])
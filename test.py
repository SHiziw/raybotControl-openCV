from MotorDriver import MotorDriver
import time
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

Motor = MotorDriver()

i2c_bus = board.I2C()

k = 0

ina1 = INA219(i2c_bus,addr=0x40)
ina2 = INA219(i2c_bus,addr=0x41)
ina3 = INA219(i2c_bus,addr=0x42)
ina4 = INA219(i2c_bus,addr=0x43)
print("ina219 test")

ina1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.bus_voltage_range = BusVoltageRange.RANGE_16V

ina2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.bus_voltage_range = BusVoltageRange.RANGE_16V

ina3.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.bus_voltage_range = BusVoltageRange.RANGE_16V

ina4.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.bus_voltage_range = BusVoltageRange.RANGE_16V

# measure and display loop
while True:
    bus_voltage1 = ina1.bus_voltage        # voltage on V- (load side)
    shunt_voltage1 = ina1.shunt_voltage    # voltage between V+ and V- across the shunt
    power1 = ina1.power
    current1 = ina1.current                # current in mA

    bus_voltage2 = ina2.bus_voltage        # voltage on V- (load side)
    shunt_voltage2 = ina2.shunt_voltage    # voltage between V+ and V- across the shunt
    power2 = ina2.power
    current2 = ina2.current                # current in mA
    
    bus_voltage3 = ina3.bus_voltage        # voltage on V- (load side)
    shunt_voltage3 = ina3.shunt_voltage    # voltage between V+ and V- across the shunt
    power3 = ina3.power
    current3 = ina3.current                # current in mA
    
    bus_voltage4 = ina4.bus_voltage        # voltage on V- (load side)
    shunt_voltage4 = ina4.shunt_voltage    # voltage between V+ and V- across the shunt
    power4 = ina4.power
    current4 = ina4.current                # current in mA
    
    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    print("PSU Voltage:{:6.3f}V    Shunt Voltage:{:9.6f}V    Load Voltage:{:6.3f}V    Power:{:9.6f}W    Current:{:9.6f}A".format((bus_voltage1 + shunt_voltage1),(shunt_voltage1),(bus_voltage1),(power1),(current1/1000)))
    print("PSU Voltage:{:6.3f}V    Shunt Voltage:{:9.6f}V    Load Voltage:{:6.3f}V    Power:{:9.6f}W    Current:{:9.6f}A".format((bus_voltage2 + shunt_voltage2),(shunt_voltage2),(bus_voltage2),(power2),(current2/1000)))
    print("PSU Voltage:{:6.3f}V    Shunt Voltage:{:9.6f}V    Load Voltage:{:6.3f}V    Power:{:9.6f}W    Current:{:9.6f}A".format((bus_voltage3 + shunt_voltage3),(shunt_voltage3),(bus_voltage3),(power3),(current3/1000)))
    print("PSU Voltage:{:6.3f}V    Shunt Voltage:{:9.6f}V    Load Voltage:{:6.3f}V    Power:{:9.6f}W    Current:{:9.6f}A".format((bus_voltage4 + shunt_voltage4),(shunt_voltage4),(bus_voltage4),(power4),(current3/1000)))
    print("")
    print("")
    if k%2:
        Motor.MotorRun(0, 'forward', 100)
        Motor.MotorRun(1, 'forward', -100)
    else: 
        Motor.MotorRun(0, 'forward', 0)
        Motor.MotorRun(1, 'forward', 0)
    k += 1
    time.sleep(1)
import os
import machine
from machine import Pin, ADC
import time
#import datetime


## INPUTS ################################

# Watering thresholds
# 1280 = overflow sensor is wet
# 1360 = wet shamrock
# 1420 = tap water
# 2400 = very dry shamrock
# 3600 = fully dry
watering_threshold = [1700,
                       1650
                       ]

# Watering time (s)
watering_time = [4,
                  3
                  ]

# Time between waterings (s)
watering_interval = 3600

# Define input pins
#button_interrupt = Pin(23, Pin.IN)
sensor_vp = ADC(Pin(36)) # yellow/green/blue
sensor_vn = ADC(Pin(39)) # brown/red/orange

# Define output pins
led = Pin(2, Pin.OUT)
pump_12 = Pin(12, Pin.OUT)
pump_13 = Pin(13, Pin.OUT)

# Interrupt counters
#n_current_interrupts = 0
#n_total_interrupts = 0


## INITIALIZE #############################

# Set range of input voltage
sensor_vp.atten(ADC.ATTN_11DB)
sensor_vn.atten(ADC.ATTN_11DB)

# Initialize output pin values
pump_12.value(0)
pump_13.value(0)

# Create sensor list
sensors = [sensor_vp,
            sensor_vn
            ]
# Define which pump each sensor controls
pumps = [pump_12,
          pump_13
          ]


## CHECK VALUES ###########################

# Print pin values and time
print("Started at:  " + str(time.localtime()))
#print("button_interrupt = " + str(button_interrupt.value()))
print("sensor_vp = " + str(sensor_vp.read()))
print("sensor_vn = " + str(sensor_vn.read()))
print("pump_12 = " + str(pump_12.value()))
print("pump_13 = " + str(pump_13.value()))


## INTERRUPTS ##############################

# Increment current interrupts
#def interrupt_callback(pin):
#  global n_current_interrupts
#  n_current_interrupts = n_current_interrupts + 1
# Trigger callback when pin value falls
#button_interrupt.irq(trigger=Pin.IRQ_RISING, handler=interrupt_callback)

# Give time to interrupt on boot
time.sleep(5)
print("Started")

# Keep track of interrupts from the button_interrupt
while True: 
  #if n_current_interrupts > 0: 
    # Don't allow simultaneous interrupts
    #state = machine.disable_irq()
    # Reset the number of current interrupts
    #n_current_interrupts = n_current_interrupts - 1
    # Calculate and print total number of interrupts
    #n_total_interrupts = n_total_interrupts + 1
    #print("Interrupt has occurred: " + str(n_total_interrupts))
    # Make sure all the pumps are turned off
    #for ipump in pumps:
    #  ipump.value(0)
    # Stop the main loop so you can reprogram the esp32, because you can't do this when things are running
    #break
    #machine.enable_irq(state)
    
  # Flash LED
  led.value(1)
  time.sleep(1)
  led.value(0)
    
  # Initialize pump and sensor status
  isPumpOn = [0]*len(sensors)
  sensorVal = [0]*len(sensors)
  
  # Check value of sensor and water plant if it is too dry
  for ind, isensor in enumerate(sensors):
    sensorVal[ind] = isensor.read()
    if isensor.read() > watering_threshold[ind]:
      # Keep track of sensor and pump information
      #print("pump # " + str(ind))
      isPumpOn[ind] = 1      
      # Turn on water for prescribed time
      pumps[ind].value(1)
      time.sleep(watering_time[ind])
      pumps[ind].value(0)
      # Delay between pumps to avoid too many things happening at once
      time.sleep(1)
  
  # Write information to spreadsheet
  # https://github.com/artem-smotrakov/esp32-weather-google-sheets
  #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  
  #print("sensor_vp = " + str(sensor_vp.read()))
  #print("sensor_vn = " + str(sensor_vn.read()))
  
  print("Measured at:  " + str(time.localtime()))
  print("Sensor values: " + (' '.join(str(x) for x in sensorVal)))
  print("Pump status: " + (' '.join(str(x) for x in isPumpOn)) + "\n")
  
  time.sleep(watering_interval)
 
print("Exited")





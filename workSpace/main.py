import os
import machine
from machine import Pin, ADC, SPI
import time
import math
#import datetime
from ST7735 import TFT
from sysfont import sysfont


## INPUTS ################################

# Watering thresholds
# LOW == WET
# HIGH == DRY
watering_threshold = [2850, # ygb
                       2400, # bro
                       2200 # kkk
                       ]

# Watering time (s)
watering_time = [5, # ygb
                  10, # bro
                  15 # kkk
                  ]

# Time between waterings (s)
watering_interval = 2*3600

# Time between measurements (s)
measuring_interval = 0.25*3600
# Number of measurements to average
n_measurements = 5

# Define input pins
#button_interrupt = Pin(23, Pin.IN)
sensor_ygb = ADC(Pin(34)) # yellow/green/blue
sensor_bro = ADC(Pin(35)) # brown/red/orange
sensor_kkk = ADC(Pin(32)) # black/black/black (outside)

# Define output pins
led = Pin(2, Pin.OUT)
pump_ygb = Pin(12, Pin.OUT)
pump_bro = Pin(13, Pin.OUT)
pump_kkk = Pin(14, Pin.OUT)

# Interrupt counters
#n_current_interrupts = 0
#n_total_interrupts = 0


## INITIALIZE #############################

# Set range of input voltage
sensor_ygb.atten(ADC.ATTN_11DB)
sensor_bro.atten(ADC.ATTN_11DB)
sensor_kkk.atten(ADC.ATTN_11DB)

# Initialize output pin values
pump_ygb.value(0)
pump_bro.value(0)
pump_kkk.value(0)

# Create sensor list
sensors = [sensor_ygb,
            sensor_bro,
            sensor_kkk
            ]
# Define which pump each sensor controls
pumps = [pump_ygb,
          pump_bro,
          pump_kkk
          ]

# LCD stuff
# VCC and GND on LCD go to 3V3 and GND on esp32
spi = SPI(2, 
          baudrate=20000000, 
          polarity=0, 
          phase=0, 
          sck=Pin(18), # CLK
          mosi=Pin(23), # DIN
          miso=Pin(4) # BL
          )
tft=TFT(spi, 
        15, # DC
        5, # RST
        2 # CS
        )
tft.initr()
tft.rgb(False)
tft.rotation(0)
screen_size = str(tft.size())


## DEFINE FUNCTIONS #######################

def get_status_as_string(sensor_values, pump_values):
  t = time.localtime()
  out_string = (
  "Measured @" + " day=" + str(t[2]) + " time=" + str(t[3]) + ":" + str(t[4])
  + "\nygb=" + str(sensor_values[0])
  + "\nbro=" + str(sensor_values[1])
  + "\nkkk=" + str(sensor_values[2])
  + "\npumps=" + str(pump_values[0])
  + " " + str(pump_values[1])
  + " " + str(pump_values[2])
  )
  return out_string
  
def print_status_to_lcd(sensor_values, pump_values=["NA", "NA", "NA"]):
  tft.fill(TFT.BLACK)
  tft.text(aPos=(0, 0), 
          aString=get_status_as_string(sensor_values, pump_values),
          aColor=TFT.WHITE, 
          aFont=sysfont, 
          aSize=1,
          nowrap=False
          )
  time.sleep_ms(1)
  
def print_status_to_terminal(sensor_values, pump_values=["NA", "NA", "NA"]):
  print(get_status_as_string(sensor_values, pump_values))
  
def read_sensor(sensor_object):
  sensor_value = []
  for i in range(n_measurements):
    sensor_value.append(sensor_object.read())
  print(str(sensor_value))
  sensor_mean = round( sum(sensor_value) / len(sensor_value) )
  return sensor_mean


## CHECK VALUES ###########################

# Print status
#print_status_to_terminal()
#print_status_to_lcd()


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
  # Don't water if sensor is maxed out, because it's probably an error
  for ind, isensor in enumerate(sensors):
    sensorVal[ind] = read_sensor(isensor)
    if (sensorVal[ind] > watering_threshold[ind]) and (sensorVal[ind] < 4095):
      # Keep track of sensor and pump information
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
  
  # Print status
  print_status_to_terminal(sensorVal, pumps)
  print_status_to_lcd(sensorVal, pumps)
  
  #time.sleep(watering_interval)
  time.sleep(measuring_interval)
  
  n_intermediate_measurements = max(math.floor(watering_interval/measuring_interval) - 1, 0)
  for i in range(n_intermediate_measurements):  
    
    for ind, isensor in enumerate(sensors):
      sensorVal[ind] = read_sensor(isensor)
      
    # Print status
    print_status_to_terminal(sensorVal)
    print_status_to_lcd(sensorVal)
    
    time.sleep(measuring_interval)
    
 
print("Exited")






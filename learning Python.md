# To activate virtual enviornment in RPI
do : 
``` source env/bin/activate```

# Threading 
It lets you run multiple processes at once 
__example:__
```python
import threading  #here
import time
from gpiozero import LED
import RPi.GPIO as GPIO  # This is the rpi-lgpio shim

# Set up gpiozero LED
gpiozero_led = LED(17)

# Set up lgpio LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)

# Define blink functions
def blink_gpiozero():
    while True:
        gpiozero_led.toggle()
        time.sleep(1)

def blink_lgpio():
    state = False
    while True:
        GPIO.output(27, state)
        state = not state
        time.sleep(1)

# Create and start threads
t1 = threading.Thread(target=blink_gpiozero)
t2 = threading.Thread(target=blink_lgpio)

t1.start()
t2.start()  
```

# Intro to gpiod
this is an example code:
```python = numberLines
import gpiod
import time

chip = gpiod.Chip("gpiochip0")
line = chip.get_line(25)
line.request(consumer="my-script", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

for i in range(5):
    line.set_value(1)
    print("ON")
    time.sleep(0.5)
    line.set_value(0)
    print("OFF")
    time.sleep(0.5)

line.release()
```
Here, `chip = gpiod.Chip("gpiochip0")` says that the RPI will use the chip (which is like the master or dispatcher with all the lines) that it is going to use gpiochip0
I should basically __always__ use gpiochip0 as it is the "master" that controlls all 54 lines
# Lines and how to configure your GPIO pins
## Scinario where all the pins are outputs
lines is basically just the pin. Line 2 would correspond to pin 2in the __BCM__ system. __Remember!!! its in BCM!!!__
- So here in Line 5 where it says `Line = chip.get_line(25)`, it is "fetching" the BCM pin 25

Then below it in line 6, `line.request(consumer="my-script", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])`. This command/function has 3 things written in it. 
- the first part `consumer="my-script"` part is __optional__ but it can help you debug stuff. It basically says that script with the name "my-script" is the one using that gpio pin. to do this, you can Bash: `gpioinfo gpiochip0` and you might see something like `line 25: "my-script" output active-high [used]` which tells you that "my-script" is using pin 25.
- the `type=gpiod.LINE_REQ_DIR_OUT` is just saying that line 2 is an output pin. if you want to configure multiple output pins, say "lines" and pick them as a group and set their default states individually :
```python 
lines = chip.get_lines([17, 22, 23])  # GPIO pins to control
lines.request(consumer="my-multiblinker", type=gpiod.LINE_REQ_DIR_OUT,default_vals=[0, 0, 0])
```
This sets them all to output pins. to change the values of the pins, you can do things like `lines.set_values([1, 0, 1])` which will turn pins 17 and 23 on
- its pretty self explanatory but `default_vals=[0]` sets their default state to 0

## To se Input/Output combinations:
If you only have one line for input/output each, you can declare it individually like this 
```python
import gpiod
import time

chip = gpiod.Chip("gpiochip0")  # Access the main GPIO chip

# 🟢 Request the input line (e.g., button on GPIO 17)
button_line = chip.get_line(17)
button_line.request(consumer="button-reader", type=gpiod.LINE_REQ_DIR_IN)
# 🔴 Request the output line (e.g., LED on GPIO 22)
led_line = chip.get_line(22)
led_line.request(consumer="led-blinker", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
```
### when you have multiple inputs/outputs:
You can do something like this:
```python
inputs = chip.get_lines([17, 23])      # Buttons
outputs = chip.get_lines([22, 24])     # LEDs

inputs.request(consumer="buttons", type=gpiod.LINE_REQ_DIR_IN)
outputs.request(consumer="leds", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0, 0])
```
You can get their values separately using 
```python
inputs.get_values()
outputs.set_values([1, 0])
```
---
# My threading code and why it doesnt work
```python = numberLines
# -*- coding: utf-8 -*-
# Pollux Labs
# polluxlabs.io
import time
import logging
import gpiod
import lgpio
import threading
# Import the previously created library
from rc522_spi_library import RC522SPILibrary, StatusCodes
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def main():
    """
    General example for reading the UID from any RFID card.
    """
    print("Starting the RFID Card Reader...")
    print("Hold any RFID card near the reader.")
    print("Press CTRL+C to exit.")
    reader = None
    try:
        # Initialize the library
        reader = RC522SPILibrary(rst_pin=22)
        # Stores the UID of the last seen card to prevent constant repetition
        last_uid = None
        while True:
            # 1. Scan for a card
            status, _ = reader.request()
            if status == StatusCodes.OK:
                # 2. If a card is in the field, get its UID (Anti-collision)
                status, uid = reader.anticoll()
                if status == StatusCodes.OK:
                    # Only act if it's a new card
                    if uid != last_uid:
                        last_uid = uid
                        # Convert UID to a readable format
                        uid_str = ":".join([f"{i:02X}" for i in uid])
                        print(f"this is the unformated UID: {uid}")
                        print("\n================================")
                        print(f"Card detected!")
                        print(f"  UID: {uid_str}")
                        print("================================")
                        print("INFO: You can now use this UID in your own code.")
                        time.sleep(2)  # Short pause to avoid flooding the output
                # If the UID could not be read, but a card is present,
                # nothing is done until the card is removed.
            else:
                # 3. If no card is in the field anymore, reset `last_uid`
                if last_uid is not None:
                    print("\nCard removed. The reader is ready for the next card.")
                    last_uid = None
            # Short pause to reduce CPU load
            time.sleep(0.1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # Make sure to release the resources at the end
        if reader:
            reader.cleanup()
            print("RC522 resources released successfully.")
if __name__ == '__main__':
    main()

#the new thing that I added

gpio = lgpio.gpiochip_open(0)  # open gpiochip0
SERVO_GPIO = 18

authorized_tags = {[100,88,201,1], [100,88,201,2], [100,88,201,3], [100,88,201,4]}

def set_servo_angle(angle):
    pulse_width = 1000 + (angle / 180) * 1000  # in microseconds
    duty_cycle = (pulse_width * 100) / 20000   # as percentage
    lgpio.tx_pwm(gpio, SERVO_GPIO, 50, duty_cycle)


def servo_control():
    print("Going to 90°")
    set_servo_angle(90)
    time.sleep(1)

    print("Going back to 0°")
    set_servo_angle(0)
    time.sleep(1)


while True:
    if uid_str in authorized_tags:
        servo_control()

t1 = threading.Thread(target=servo_control)
t2 = threading.Thread(target=main)

t1.start()
t2.start()
```
So there are a couple issues here. 
1. I can do `{[XXX], [XXX]}` in line 71 its like a thing with lists. you should just make a "list of lists" like `[(XXX), (xxx)]`
2. thhe whole threading structure is wrong. currently, the `def servo_control()` is set to run concurrently with the rfid scanning code. so the servo will just go to 90 deg, come back once and finish. 
3. since the `uid` term is in `def main()`, a different function that isnt in `main()` can't acess it. 
## queue
to use something in one function in another function/thread, use queue
to start, you need to put `from queue import Queue`
to put stuff in the queue to use later, you do `queue.put(data)`, and to retreive it, do `queue.get()   
### example code of this working
```python 
import time
import logging
import lgpio
import threading
from queue import Queue
from rc522_spi_library import RC522SPILibrary, StatusCodes

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Servo setup
gpio = lgpio.gpiochip_open(0)
SERVO_GPIO = 18

def set_servo_angle(angle):
    pulse_width = 1000 + (angle / 180) * 1000  # µs
    duty_cycle = (pulse_width * 100) / 20000
    lgpio.tx_pwm(gpio, SERVO_GPIO, 50, duty_cycle)

def servo_control():
    print("🟠 Moving to 90°")
    set_servo_angle(90)
    time.sleep(1)
    print("🔵 Returning to 0°")
    set_servo_angle(0)
    time.sleep(1)

# UID queue and authorized tags
uid_queue = Queue()
authorized_tags = {
    (100, 88, 201, 1),
    (100, 88, 201, 2),
    (100, 88, 201, 3),
    (100, 88, 201, 4)
}

# 🔍 Thread 1: RFID scanner
def tag_scanner():
    reader = RC522SPILibrary(rst_pin=22)
    last_uid = None
    try:
        while True:
            status, _ = reader.request()
            if status == StatusCodes.OK:
                status, uid = reader.anticoll()
                if status == StatusCodes.OK and uid != last_uid:
                    last_uid = uid
                    uid_tuple = tuple(uid)
                    uid_str = ":".join([f"{i:02X}" for i in uid])
                    print(f"\n🆕 UID detected: {uid_str}")
                    uid_queue.put(uid_tuple)  # send to processor
                    time.sleep(2)  # prevent spam
            else:
                last_uid = None
            time.sleep(0.1)
    except Exception as e:
        logging.error(f"RFID Error: {e}")
    finally:
        reader.cleanup()
        print("🔌 RFID reader cleaned up.")

# 🤖 Thread 2: UID processor + Servo controller
def uid_processor():
    while True:
        uid = uid_queue.get()
        if uid in authorized_tags:
            print(f"✅ Authorized UID: {uid}")
            servo_control()
        else:
            print(f"❌ Unauthorized UID: {uid}")
        uid_queue.task_done()

# 🚀 Start threads
scanner_thread = threading.Thread(target=tag_scanner, daemon=True)
processor_thread = threading.Thread(target=uid_processor, daemon=True)

scanner_thread.start()
processor_thread.start()

try:
    while True:
        time.sleep(1)  # keep main thread alive
except KeyboardInterrupt:
    print("\n🛑 Exiting...")
finally:
    lgpio.tx_pwm(gpio, SERVO_GPIO, 0, 0)
    lgpio.gpiochip_close(gpio)
    print("Cleanup complete.")
```

# Automate git add, commit, push
## The short cut is :
```
ctrl + alt + p
```


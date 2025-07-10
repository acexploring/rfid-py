import threading
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
import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    while True:
        print("Place your RFID tag near the reader...")
        id, text = reader.read()
        print(f"ID: {id}")
        print(f"Text on tag: {text}")
        time.sleep(1)  # Wait for a second before the next read
finally:
    GPIO.cleanup()
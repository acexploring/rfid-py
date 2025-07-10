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


import time
import logging
import lgpio
from rc522_spi_library import RC522SPILibrary, StatusCodes

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Servo setup
gpio = lgpio.gpiochip_open(0)
SERVO_GPIO = 18
lgpio.gpio_claim_output(gpio, SERVO_GPIO, 0)  # Ensure the pin is set to output mode

def set_servo_angle(angle):
    pulse_width = 1000 + (angle / 180) * 1000  # µs
    duty_cycle = (pulse_width * 100) / 20000
    lgpio.tx_pwm(gpio, SERVO_GPIO, 50, duty_cycle)

def servo_control():
    set_servo_angle(0)  # Initialize servo to 0°
    print("Going to 90°")
    set_servo_angle(90)
    time.sleep(2)
    print("Returning to 0°")
    set_servo_angle(0)
    time.sleep(2)

# List of authorized UIDs as tuples
authorized_tags = [
    (100, 88, 201, 1),
    (100, 88, 201, 2),
    (100, 88, 201, 3),
    (100, 88, 201, 4)
]

def main():
    print("Starting the RFID Card Reader...")
    print("Hold any RFID card near the reader.")
    print("Press CTRL+C to exit.")

    reader = None
    last_uid = None

    try:
        reader = RC522SPILibrary(rst_pin=22)
        while True:
            status, _ = reader.request()
            if status == StatusCodes.OK:
                status, uid = reader.anticoll()
                if status == StatusCodes.OK and uid != last_uid:
                    last_uid = uid
                    uid_tuple = tuple(uid)
                    uid_str = ":".join([f"{i:02X}" for i in uid])
                    print(f"\nDetected UID (raw): {uid}")
                    print("================================")
                    print(f"UID: {uid_str}")
                    print("================================")

                    if uid_tuple in authorized_tags:
                        print("✅ Authorized tag detected!")
                        servo_control()
                    else:
                        print("❌ Unauthorized tag.")
                    time.sleep(2)
            else:
                if last_uid is not None:
                    print("\nCard removed. Ready for next scan.")
                    last_uid = None

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if reader:
            reader.cleanup()
        lgpio.gpio_claim_output(gpio, SERVO_GPIO, 0)  # reclaim control and reset pin low
        lgpio.gpiochip_close(gpio)
        print("Resources cleaned up.")

if __name__ == '__main__':
    main()
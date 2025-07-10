import time
import logging
import lgpio
from rc522_spi_library import RC522SPILibrary, StatusCodes

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Servo setup
gpio = lgpio.gpiochip_open(0)
SERVO_GPIO = 18
TRANSISTOR_GPIO = 17  # Example GPIO for TRANSISTOR control, if needed
lgpio.gpio_claim_output(gpio, SERVO_GPIO, 0)  # Ensure the pin is set to output mode
lgpio.gpio_claim_output(gpio, TRANSISTOR_GPIO, 0)
def set_servo_angle(angle):
    # Clamp angle to range
    angle = max(0, min(angle, 180))
    
    min_pulse = 600    # microseconds (try 500–600)
    max_pulse = 2200   # microseconds (try 2200–2400)

    pulse_width = min_pulse + (angle / 180) * (max_pulse - min_pulse)
    duty_cycle = (pulse_width * 100) / 20000  # for 50 Hz

    lgpio.tx_pwm(gpio, SERVO_GPIO, 50, round(duty_cycle, 1))


def servo_control():
    lgpio.gpio_write(gpio, TRANSISTOR_GPIO, 1)
    time.sleep(0.1)

    print("Going to 90°")
    set_servo_angle(90)
    time.sleep(1.2)

    lgpio.gpio_write(gpio, TRANSISTOR_GPIO, 0)
    time.sleep(3)

    print("Returning to 0°")
    lgpio.gpio_write(gpio, TRANSISTOR_GPIO, 1)
    time.sleep(0.1)

    set_servo_angle(0)
    time.sleep(1.2)

    # Let PWM continue briefly
    time.sleep(0.3)
    lgpio.tx_pwm(gpio, SERVO_GPIO, 0, 0)
    time.sleep(0.3)
    # Now cut power to servo
    lgpio.gpio_write(gpio, TRANSISTOR_GPIO, 0)




# List of authorized UIDs as tuples
authorized_tags = [
    (100, 88, 201, 1),
    (100, 88, 201, 2),
    (100, 88, 201, 3),
    (100, 88, 201, 4)
]

pulse_width_0 = 1000  # in microseconds for 0 degrees
duty_cycle_for_0_deg = (pulse_width_0 * 100) / 20000


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
                        reader.cleanup()
                        reader.initialize()  # Reinitialize the reader after cleanup
                        time.sleep(0.1)
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
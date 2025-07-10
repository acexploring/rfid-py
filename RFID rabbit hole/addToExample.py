import threading
import time
import lgpio
import gpiod

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
        def servo_control():


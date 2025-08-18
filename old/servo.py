import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

servo = GPIO.PWM(servoPIN, 50)  # GPIO 17 for PWM with 50Hz
servo.start(2.5)  # Initialization

def move_servo_to_angle(angle):
    duty = 2.5 + (angle / 18.0)  # calculate the duty cycle for the given angle
    servo.ChangeDutyCycle(duty)
    time.sleep(0.04)

try:
    for angle in range(90, 0, -1):  # slowly pan to 0 degrees
        move_servo_to_angle(angle)
    for angle in range(0, 180):  # slowly pan to 180 degrees
        move_servo_to_angle(angle)
    for angle in range(180, 90, -1):  # slowly pan back to 90 degrees
        move_servo_to_angle(angle)
    move_servo_to_angle(90)  # stop at 90 degrees
except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()

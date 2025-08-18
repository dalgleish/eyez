import RPi.GPIO as GPIO

# RIGHT EYE
# GPIO 17 for PWM with 50Hz
rightEyeServoPIN = 17

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rightEyeServoPIN, GPIO.OUT)
    rightServo = GPIO.PWM(rightEyeServoPIN, 50)
    rightServo.start(2.5)  

    current_angle = 90
    target_angle = 90

    while True:
        try:
            # returns a value from 0 to 32
            person_column = detect_person()
            target_angle = translate_to_angle(person_column)
            print(f'target_angle {target_angle}')
            if target_angle is not None:
                move_servo_to_angle(rightServo, current_angle, target_angle)
                current_angle = target_angle


def translate_to_angle(number):
    if number is None:
        return
    if 0 <= number <= 32:
        angle = (number / 32.0) * 180.0
        return angle

def move_servo_to_angle(servo, current_angle, target_angle, step=1, delay=0.02):
    if current_angle is None or target_angle is None:
        return
    
    # Determine the direction of movement
    if target_angle > current_angle:
        angle_range = range(current_angle, target_angle + 1, step)
    else:
        angle_range = range(current_angle, target_angle - 1, -step)
    print(f'angle_range {angle_range}')

    # Move the servo in small steps to the target angle
    for angle in angle_range:
        duty = 2.5 + (angle / 18.0)
        print(f'moving: duty {duty}')
        servo.ChangeDutyCycle(duty)
        time.sleep(delay)


if __name__ == '__main__':
    main()

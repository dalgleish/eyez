import pigpio
import time

# right
servo = 18

# left
servo = 12

# more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth

pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)

pwm.set_PWM_frequency( servo, 50 )

print( "Look left (0 degrees)" )
pwm.set_servo_pulsewidth( servo, 700 ) ;
time.sleep( 3 )

# turning off servo
pwm.set_PWM_dutycycle( servo, 0 )
pwm.set_PWM_frequency( servo, 0 )
#!/usr/bin/env python3
"""
Servo Test Program for Miuzei MS24-F 20kg Digital Servo
Using pigpio library - more precise PWM control
Connected to GPIO Pin 17 on Raspberry Pi 3 B+
"""

import pigpio
import time

# Configuration
# SERVO_PIN = 10 # right
SERVO_PIN = 9 # left

def angle_to_pulsewidth(angle):
    """
    Convert angle (0-180) to pulse width in microseconds
    Most servos: 0° = 1000μs, 90° = 1500μs, 180° = 2000μs
    """
    pulse_width = 1000 + (angle / 180.0) * 1000
    return int(pulse_width)

def move_to_angle(pi, angle, delay=0.5):
    """Move servo to specific angle"""
    pulse_width = angle_to_pulsewidth(angle)
    print(f"Moving to {angle}° (pulse width: {pulse_width}μs)")
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    time.sleep(delay)

def test_sequence(pi):
    """Run a series of test movements"""
    print("\n=== Starting Servo Test Sequence ===\n")
    
    # Test 1: Move to center position
    print("Test 1: Center position (90°)")
    move_to_angle(pi, 90, 1)
    
    # Test 2: Move to extremes
    print("\nTest 2: Full range test")
    print("Moving to 0°...")
    move_to_angle(pi, 0, 1)
    print("Moving to 180°...")
    move_to_angle(pi, 180, 1)
    print("Returning to center...")
    move_to_angle(pi, 90, 1)
    
    # Test 3: Sweep motion
    print("\nTest 3: Sweep motion (0° to 180°)")
    for angle in range(0, 181, 15):
        move_to_angle(pi, angle, 0.2)
    
    # Test 4: Reverse sweep
    print("\nTest 4: Reverse sweep (180° to 0°)")
    for angle in range(180, -1, -15):
        move_to_angle(pi, angle, 0.2)
    
    # Test 5: Return to center
    print("\nTest 5: Return to neutral position")
    move_to_angle(pi, 90, 1)

def interactive_mode(pi):
    """Allow manual servo control"""
    print("\n=== Interactive Mode ===")
    print("Enter angle (0-180) or 'q' to quit")
    
    while True:
        try:
            user_input = input("\nAngle: ").strip()
            if user_input.lower() == 'q':
                break
            
            angle = float(user_input)
            if 0 <= angle <= 180:
                move_to_angle(pi, angle, 0.5)
            else:
                print("Please enter an angle between 0 and 180")
        except ValueError:
            print("Invalid input. Enter a number between 0-180 or 'q' to quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    """Main program"""
    print("=" * 50)
    print("Miuzei MS24-F Servo Test Program (pigpio)")
    print(f"GPIO Pin: {SERVO_PIN}")
    print("=" * 50)
    
    # Initialize pigpio
    pi = pigpio.pi()
    
    if not pi.connected:
        print("ERROR: Could not connect to pigpio daemon")
        print("Make sure pigpiod is running: sudo pigpiod")
        return

    pi.set_mode(SERVO_PIN, pigpio.OUTPUT) 
    
    try:
        # Run automated tests
        test_sequence(pi)
        
        # Enter interactive mode
        interactive_mode(pi)
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        # Turn off servo
        print("\nStopping servo...")
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()
        print("Cleanup complete")

if __name__ == "__main__":
    main()

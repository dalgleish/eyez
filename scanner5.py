#!/usr/bin/env python

import seeed_mlx9064x
import numpy as np
import cv2
import time
import signal
import sys
import pigpio


def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


class Eyez:
    def __init__(self, right_servo_pin=18, left_servo_pin=12, temperature_threshold=30):
        self.right_servo_pin = right_servo_pin
        self.left_servo_pin = left_servo_pin

        # Quadrant mapping for servos
        self.quadrants = {
            self.right_servo_pin: [60 * i + 600 for i in range(32)],
            self.left_servo_pin: [60 * i + 600 for i in range(32)],
        }

        self.temperature_threshold = temperature_threshold
        self.current_column = 16  # Start at center
        self.position_buffer = []
        self.buffer_size = 5  # For smoothing
        self.mlx = None  # Thermal camera
        self.width, self.height = 32, 24
        # image output, for debugging
        self.frame_counter = 0

    def turn_off_servos(self):
        if self.pwm is not None:
            self.pwm.set_PWM_dutycycle(self.right_servo_pin, 0)
            self.pwm.set_PWM_frequency(self.right_servo_pin, 0)
            self.pwm.set_PWM_dutycycle(self.left_servo_pin, 0)
            self.pwm.set_PWM_frequency(self.left_servo_pin, 0)

    def cleanup(self):
        print('Cleaning up...')
        self.turn_off_servos()

    def translate_to_quadrant(self, column, servo_pin):
        if column is None or column < 0 or column >= 32:
            return None
        return self.quadrants[servo_pin][int(column)]

    def move_servos(self, target_column):
        pulse_width_left = self.translate_to_quadrant(target_column, self.left_servo_pin)
        pulse_width_right = self.translate_to_quadrant(target_column, self.right_servo_pin)

        if pulse_width_left is not None and pulse_width_right is not None:
            self.pwm.set_servo_pulsewidth(self.left_servo_pin, pulse_width_left)
            self.pwm.set_servo_pulsewidth(self.right_servo_pin, pulse_width_right)
            time.sleep(0.1)
            self.turn_off_servos()


    def smooth_position(self, new_position):
        self.position_buffer.append(new_position)
        if len(self.position_buffer) > self.buffer_size:
            self.position_buffer.pop(0)
        return int(sum(self.position_buffer) / len(self.position_buffer))


    def detect_person(self, frame_data):
        # Convert frame to NumPy array and reshape
        current_frame = np.array(frame_data).reshape(self.height, self.width).astype(float)

        # Remove the first 4 rows (mostly sky and streetlights)
        current_frame = current_frame[4:, :]  # Now 20x32

        # self.print_frame_matrix(current_frame)

        # element-wise comparison
        person_mask = current_frame > self.temperature_threshold
        # Create binary mask where temperatures above the threshold are 1
        person_mask = person_mask.astype(np.uint8) * 255

        # Apply morphological operations to reduce noise
        kernel = np.ones((3, 3), np.uint8)
        person_mask = cv2.erode(person_mask, kernel, iterations=1)
        person_mask = cv2.dilate(person_mask, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(person_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Convert the mask to a color image for contour drawing
        color_mask = cv2.cvtColor(person_mask, cv2.COLOR_GRAY2BGR)

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cX = int(M['m10'] / M['m00'])
            
                # Draw contours on the color mask
                cv2.drawContours(color_mask, contours, -1, (0, 255, 0), 2)  # Green contours
                
                # Save the image with contours
                filename = f'frames/frame_{self.frame_counter}.png'
                cv2.imwrite(filename, color_mask)

                return cX
        return None

    def read_frame(self):
        frame = [0] * 768  # 32x24

        try:
            self.mlx.getFrame(frame)
        except Exception as e:
            frame = None
        finally:
            return frame

    def print_frame_matrix(self, frame_data):
        np.set_printoptions(precision=1, suppress=True)
        print(frame_data)


    def run(self):
        print('Initialize pigpio PWM')
        self.pwm = pigpio.pi()
        self.pwm.set_mode(self.right_servo_pin, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.right_servo_pin, 50)
        self.pwm.set_mode(self.left_servo_pin, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.left_servo_pin, 50)
        time.sleep(1)

        print('Initialize thermal camera')
        self.mlx = seeed_mlx9064x.grove_mxl90640()
        self.mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ
        time.sleep(1)

        try:
            print('Start main loop')
            while True:
                frame = self.read_frame()
                # Couldn't read frame
                if frame is None:
                    time.sleep(0.5)
                    continue

                self.frame_counter += 1
                column = self.detect_person(frame)
                if column is None:
                    continue  # No person detected

                print(f'detected_column {column}')

                # Smooth the detected position
                target_column = self.smooth_position(column)

                print(f'target_column {target_column}')

                # Only move servos if the target position changed significantly
                if abs(self.current_column - target_column) > 1:
                    print(f'target_column {target_column} moving...')
                    self.move_servos(target_column)
                    self.current_column = target_column
                else:
                    print(f'target_column {target_column} too close to {self.current_column}')

        except KeyboardInterrupt:
            self.cleanup()
            sys.exit(0)

    def cleanup(self):
        return

if __name__ == '__main__':
    print('Initialize Eyez')
    eyez = Eyez()
    eyez.run()

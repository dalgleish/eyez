#!/usr/bin/env python

import seeed_mlx9064x
import numpy as np
import cv2
import time
import os
import signal
import sys
import pigpio

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# output images and stich together a video for debugging
make_video = True

pwm = None

# RIGHT EYE
# GPIO pin for PWM with 50Hz
right_servo = 18
left_servo = 12

width, height = 32, 24

quadrants = {
    # Right Eye Range
    # 32 possible columns
    # ~60 pulse widths between 600 and 2500 for standard servo
    right_servo: [60 * i + 600 for i in range(32)],
    # Right Eye Range
    # 32 possible columns
    # ~60 pulse widths between 600 and 2500 for standard servo
    left_servo: [60 * i + 600 for i in range(32)],
}

def translate_to_quadrant(column, servo):
    if column is None:
        return

    return quadrants[servo][int(column)]

def cleanup():
    print("Cleaning up...")

    if pwm is not None:
        # turning off servos
        pwm.set_PWM_dutycycle(right_servo, 0)
        pwm.set_PWM_frequency(right_servo, 0)
        pwm.set_PWM_dutycycle(left_servo, 0)
        pwm.set_PWM_frequency(left_servo, 0)
    if make_video:
        create_video('frames', 'output_video.avi')
    clear_frames_directory()

def move_servos(pwm, target_column):
    pulse_width_left = translate_to_quadrant(target_column, left_servo)
    pulse_width_right = translate_to_quadrant(target_column, right_servo)

    if pulse_width_left is not None and pulse_width_right is not None:
        pwm.set_servo_pulsewidth(right_servo, pulse_width_right)
        pwm.set_servo_pulsewidth(left_servo, pulse_width_left)
        time.sleep(0.1)
        # turning off servos
        pwm.set_PWM_dutycycle(right_servo, 0)
        pwm.set_PWM_frequency(right_servo, 0)
        pwm.set_PWM_dutycycle(left_servo, 0)
        pwm.set_PWM_frequency(left_servo, 0)

def parse_frame(frame):
    # Convert frame data to NumPy array and convert to float type
    _frame = np.array(frame).reshape(height, width).astype(float)

    # Remove the first 6 rows (mostly sky and streetlights)
    _frame = _frame[6:, :]  # Now 18x32

    return _frame


def main():
    
    # START SERVO SETUP ##################
    # more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
    pwm = pigpio.pi()
    pwm.set_mode(right_servo, pigpio.OUTPUT)
    pwm.set_PWM_frequency(right_servo, 50)

    # pwm = pigpio.pi()
    pwm.set_mode(left_servo, pigpio.OUTPUT)
    pwm.set_PWM_frequency(left_servo, 50)
    # END SERVO SETUP

    mlx = seeed_mlx9064x.grove_mxl90640()
    frame = [0] * 768  # 32x24


    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ
    time.sleep(1)
    
    frame_count = 0
    current_column = 16
    target_column = 16
    current_frame = None
    prev_frame = parse_frame(frame)

    while True:
        try:
            start_time = time.time()
            try:
                mlx.getFrame(frame)
            except Exception as e:
                continue

            current_frame = parse_frame(frame)

            # Normalize data to a fixed range (for speed)
            current_frame = cv2.normalize(current_frame, None, 0, 255, cv2.NORM_MINMAX)
            current_frame = np.uint8(current_frame)

            target_column = detect_human_column(prev_frame, current_frame)
            prev_frame = current_frame

            # If nothing changed, do nothing
            if target_column is None or current_column == target_column:
                print('column didn\'t change')
                continue

            print('column:', target_column)
            move_servos(pwm, target_column)

            # Save normalized frame
            if make_video:
                save_image(current_frame, f'frames/normalized_{frame_count}.png')
                frame_count += 1

            current_column = target_column

            output_fps(start_time)
        except KeyboardInterrupt:
            cleanup()
            sys.exit(0)
            break


def detect_human_column(prev_frame, curr_frame, threshold=5):
  """Detects the column where a human is most likely located.

  Args:
    prev_frame: The previous frame as a NumPy array.
    curr_frame: The current frame as a NumPy array.
    threshold: The threshold for considering a pixel as part of a human.

  Returns:
    The index of the column where the human is most likely located.
  """

  # Calculate absolute difference
  diff = np.abs(curr_frame - prev_frame)

  # Thresholding
  mask = diff > threshold

  # Column-wise summation
  col_sums = np.sum(mask, axis=0)

  # Maximum column index
  human_col = np.argmax(col_sums)

  return human_col


## DEBUGGING ####################################

def output_fps(start_time):
    # Frames per second
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    print(f'FPS: {fps:.2f}')

def clear_frames_directory(directory='frames/'):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f'Removed {file_path}')
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                print(f'Removed directory {file_path}')
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def save_image(data, filename):
    cv2.imwrite(filename, data)


def create_video(image_folder, output_video, fps=10):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()


## ENTRYPOINT ####################################
if __name__ == '__main__':
    clear_frames_directory()
    main()

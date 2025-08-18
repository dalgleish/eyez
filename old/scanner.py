import seeed_mlx9064x
import numpy as np
import cv2
import time

def main():
    mlx = seeed_mlx9064x.grove_mxl90640()
    frame = [0] * 768  # 32x24
    width, height = 32, 24

    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ

    last_fps_time = time.time()  # Timing Recording for FPS Output

    prev_frame = None  # Variable to store previous frame data

    time.sleep(1)
    while True:
        start_time = time.time()

        try:
            mlx.getFrame(frame)
        except Exception as e:
            continue

        # Convert frame data to NumPy array and convert to float type
        current_frame = np.array(frame).reshape(height, width).astype(float)

        # Normalize data to a fixed range (for speed)
        normalized_data = cv2.normalize(current_frame, None, 0, 255, cv2.NORM_MINMAX)
        normalized_data = np.uint8(normalized_data)

        end_time = time.time()
        fps = 1 / (end_time - start_time)

        if prev_frame is not None:
            person_column = find_person_column(prev_frame, normalized_data)
            print("Person is likely in column:", person_column)

        # Save current frame as previous frame
        prev_frame = normalized_data.copy()
        
        # print(normalized_data)
        # Display FPS text on image (top left)
        print(f'FPS: {fps:.2f}')

def find_person_column(prev_frame, curr_frame):
    width = 32
    height = 24
    col_diff_sums = [0] * width

    for col in range(width):
        for row in range(height):
            # Calculate the difference between each pixel in the current frame and the previous frame
            current_pixel = curr_frame[row, col]
            previous_pixel = prev_frame[row, col]

            col_diff_sums[col] += abs(current_pixel - previous_pixel)

    person_col = col_diff_sums.index(max(col_diff_sums))
    return person_col

if __name__ == '__main__':
    main()

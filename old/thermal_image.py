import seeed_mlx9064x
import numpy as np
import cv2
import time

def main():
    mlx = seeed_mlx9064x.grove_mxl90640()
    frame = [0] * 768  # 32x24 해상도
    width, height = 32, 24

    # OpenCV Windows Settings
    cv2.namedWindow('Thermal Camera', cv2.WINDOW_NORMAL)

    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ

    target_width, target_height = 640, 480  # Change target resolution
    last_fps_time = time.time()  # Timing Recording for FPS Output

    prev_frame = None  # Variable to store previous frame data

    while True:
        start_time = time.time()

        # Reading frames from the sensor
        try:
            # fails here
            mlx.getFrame(frame)
        except Exception as e:
            print(f"Error reading frame: {e}")
            continue

        # Convert frame data to NumPy array and convert to float type
        current_frame = np.array(frame).reshape(height, width).astype(float)

        # # Compare with past data
        # if prev_frame is not None:
        #     for i in range(height):
        #         for j in range(width):
        #             # Calculate the difference between each value of the current frame and the previous frame
        #             if abs(current_frame[i, j] - prev_frame[i, j]) <= 0.8:
        #                 # If the difference is less than 5, use the data from the previous frame.
        #                 current_frame[i, j] = prev_frame[i, j]

        # Normalize data to a fixed range (for speed)
        normalized_data = cv2.normalize(current_frame, None, 0, 255, cv2.NORM_MINMAX)
        normalized_data = np.uint8(normalized_data)

        # # If the change is less than 10% compared to the previous frame, use the previous value.
        # if prev_normalized_data is not None:
        #     for i in range(height):
        #         for j in range(width):
        #             # Calculate the difference between each pixel in the current frame and the previous frame
        #             current_pixel = normalized_data[i, j]
        #             previous_pixel = prev_normalized_data[i, j]

        #             # If the difference between pixels is less than 10%, keep the previous value.
        #             if abs(current_pixel - previous_pixel) / 255 < 0.05:
        #                 normalized_data[i, j] = previous_pixel

        # Apply colormap (using COLORMAP_JET)
        color_mapped_data = cv2.applyColorMap(normalized_data, cv2.COLORMAP_JET)

        # Enlarge image size by 5x (change interpolation method to INTER_NEAREST to improve speed)
        resized_image = cv2.resize(
            color_mapped_data,
            (target_width, target_height),
            interpolation=cv2.INTER_CUBIC )

        # Apply Bilateral Filter (remove noise while maintaining edges)
        #filtered_image = cv2.bilateralFilter(resized_image, 9, 75, 75)

        # Apply Gaussian filter (kernel size: 5x5, standard deviation: 0)
        #filtered_image = cv2.GaussianBlur(resized_image, (5, 5), 0)

        filtered_image = cv2.medianBlur(resized_image, 15)

        end_time = time.time()
        fps = 1 / (end_time - start_time)

        # Display FPS text on image (top left)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(filtered_image, f'FPS: {fps:.2f}', (10,30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


        # Display image
        cv2.imshow('Thermal Camera', filtered_image)

        # # Save current frame as previous frame
        # prev_normalized_data = normalized_data.copy()
        
        # # Save current frame as previous frame
        # prev_frame = current_frame.copy()

        # Detect key input after 1ms wait (press q to exit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
       

    # Exit OpenCV window
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

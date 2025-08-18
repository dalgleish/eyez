import seeed_mlx9064x
import numpy as np
import cv2
import time


def main():
    mlx = seeed_mlx9064x.grove_mxl90640()
    frame = [0] * 768  # 32x24
    width, height = 32, 24
    # Initialize background model with zeros
    background_model = np.zeros((24, 32), np.uint8)

    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ
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

        background_model = update_background_model(normalized_data, background_model)
        person_column = detect_person(normalized_data, background_model)
        print("Person is likely in column:", person_column)
        
        #output_fps(start_time)


def output_fps(start_time):
    # Frames per second
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    print(f'FPS: {fps:.2f}')

def update_background_model(frame, background_model, alpha=0.05):
    return cv2.addWeighted(frame, alpha, background_model, 1 - alpha, 0)

def detect_person(frame, background_model, threshold=25):
    diff = cv2.absdiff(frame, background_model)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        person_column = x + w // 2
        return person_column

    return None

if __name__ == '__main__':
    main()

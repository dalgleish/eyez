import seeed_mlx9064x
import numpy as np
import cv2
import time
import os
import signal
import sys

make_video = False

def cleanup():
    print("Cleaning up before exiting...")
    if make_video:
        create_video('frames', 'output_video.avi')
    clear_frames_directory()


def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    mlx = seeed_mlx9064x.grove_mxl90640()
    frame = [0] * 768  # 32x24
    width, height = 32, 24
    # Initialize background model with zeros
    background_model = np.zeros((24, 32), np.uint8)
    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_4_HZ
    time.sleep(1)
    
    # Buffer for smoothing
    buffer_size = 5
    frames_buffer = []
    frame_count = 0

    while True:
        try:
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

            # Add current frame to buffer
            frames_buffer.append(normalized_data)
            if len(frames_buffer) > buffer_size:
                frames_buffer.pop(0)
            
            # Average frames in buffer for smoothing
            smoothed_frame = np.mean(frames_buffer, axis=0).astype(np.uint8)
            
            background_model = update_background_model(smoothed_frame, background_model)
            person_column = detect_person(smoothed_frame, background_model)

            # Save normalized frame
            if make_video:
                save_image(normalized_data, f'frames/normalized_{frame_count}.png')

            # Remove outliers (optional)
            if person_column is not None:
                print("Person is likely in column:", person_column)

            frame_count += 1
            # output_fps(start_time)
        except KeyboardInterrupt:
            # Optional: Additional handling if needed
            break

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
    clear_frames_directory()
    main()

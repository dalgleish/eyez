import seeed_mlx9064x
import numpy as np
import cv2
import time

CHIP_TYPE = 'MLX90640'  # 또는 'MLX90641'

def main():
    # MLX90640 또는 MLX90641 초기화
    if CHIP_TYPE == 'MLX90641':
        mlx = seeed_mlx9064x.grove_mxl90641()
        frame = [0] * 192  # 16x12 해상도
        width, height = 16, 12
    elif CHIP_TYPE == 'MLX90640':
        mlx = seeed_mlx9064x.grove_mxl90640()
        frame = [0] * 768  # 32x24 해상도
        width, height = 32, 24
    else:
        raise ValueError("CHIP_TYPE must be either 'MLX90640' or 'MLX90641'")

    # OpenCV 윈도우 설정
    cv2.namedWindow('Thermal Camera', cv2.WINDOW_NORMAL)

    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_8_HZ  # refresh_rate 설정

    target_width, target_height = 640, 480  # 변경할 목표 해상도
    last_fps_time = time.time()  # FPS 출력을 위한 타이밍 기록

    prev_frame = None  # 이전 프레임 데이터를 저장할 변수

    while True:
        start_time = time.time()

        # 센서에서 프레임 읽기
        try:
            mlx.getFrame(frame)
        except ValueError as e:
            print(f"Error reading frame: {e}")
            continue

        # 프레임 데이터를 NumPy 배열로 변환하고, float 타입으로 변환
        current_frame = np.array(frame).reshape(height, width).astype(float)

        # # 과거 데이터와 비교
        # if prev_frame is not None:
        #     for i in range(height):
        #         for j in range(width):
        #             # 현재 프레임과 이전 프레임의 각 값 차이 계산
        #             if abs(current_frame[i, j] - prev_frame[i, j]) <= 0.8:
        #                 # 차이가 5 이하인 경우 이전 프레임의 데이터를 사용
        #                 current_frame[i, j] = prev_frame[i, j]

        # 데이터를 고정된 범위로 정규화 (속도 향상)
        normalized_data = cv2.normalize(current_frame, None, 0, 255, cv2.NORM_MINMAX)
        normalized_data = np.uint8(normalized_data)

        # # 이전 프레임과 비교하여 변화가 10% 이하인 경우 이전 값을 사용
        # if prev_normalized_data is not None:
        #     for i in range(height):
        #         for j in range(width):
        #             # 현재 프레임과 이전 프레임의 각 픽셀 차이 계산
        #             current_pixel = normalized_data[i, j]
        #             previous_pixel = prev_normalized_data[i, j]

        #             # 픽셀 간 차이가 10% 이하일 경우 이전 값 유지
        #             if abs(current_pixel - previous_pixel) / 255 < 0.05:
        #                 normalized_data[i, j] = previous_pixel

        # 컬러맵 적용 (COLORMAP_JET 사용)
        color_mapped_data = cv2.applyColorMap(normalized_data, cv2.COLORMAP_JET)

        # 이미지 크기 5배로 확대 (보간 방식을 INTER_NEAREST로 변경해 속도 향상)
        resized_image = cv2.resize(color_mapped_data, (target_width, target_height), interpolation=cv2.INTER_CUBIC )

        # Bilateral 필터 적용 (엣지를 유지하면서 노이즈 제거)
        #filtered_image = cv2.bilateralFilter(resized_image, 9, 75, 75)

        # 가우시안 필터 적용 (커널 크기: 5x5, 표준 편차: 0)
        #filtered_image = cv2.GaussianBlur(resized_image, (5, 5), 0)

        filtered_image = cv2.medianBlur(resized_image, 15)


        end_time = time.time()
        fps = 1 / (end_time - start_time)

        # FPS 텍스트를 이미지에 표시(왼쪽 상단)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(filtered_image, f'FPS: {fps:.2f}', (10,30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


        # 이미지 표시
        cv2.imshow('Thermal Camera', filtered_image)

        # # 현재 프레임을 이전 프레임으로 저장
        # prev_normalized_data = normalized_data.copy()
        
        # # 현재 프레임을 이전 프레임으로 저장
        # prev_frame = current_frame.copy()

        # 1ms 대기 후 키 입력 감지 (q를 누르면 종료)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
       

    # OpenCV 윈도우 종료
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

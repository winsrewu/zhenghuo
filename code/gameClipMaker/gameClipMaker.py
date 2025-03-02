import cv2
import numpy as np
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from collections import deque

def extract_frames_with_condition(input_video, output_video, target_image, target_image_2, mask, mask_2, threshold=10, 
                                  before_seconds=1, after_seconds=1, before_seconds_2=1, after_seconds_2=1, max_frames=-1, num_workers=4):
    # 打开输入视频
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise ValueError("无法打开输入视频文件")

    # 获取视频的基本信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_to_process = total_frames if max_frames == -1 else min(total_frames, max_frames)

    # 计算前后需要保留的帧数
    before_frames = int(before_seconds * fps)
    after_frames = int(after_seconds * fps)

    before_frames_2 = int(before_seconds_2 * fps)
    after_frames_2 = int(after_seconds_2 * fps)

    # 遮罩预处理
    if target_image.shape[:2] != mask.shape[:2]:
        raise ValueError("目标图片和遮罩的尺寸必须相同")
    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask_bool = mask == 0
    if not np.any(mask_bool):
        raise ValueError("遮罩区域为空，请检查遮罩图片")
    target_flat = target_image[mask_bool].astype(np.float16)

    if target_image_2.shape[:2] != mask_2.shape[:2]:
        raise ValueError("目标图片和遮罩的尺寸必须相同")
    if len(mask_2.shape) == 3:
        mask_2 = cv2.cvtColor(mask_2, cv2.COLOR_BGR2GRAY)
    mask_bool_2 = mask_2 == 0
    if not np.any(mask_bool_2):
        raise ValueError("遮罩区域为空，请检查遮罩图片")
    target_flat_2 = target_image_2[mask_bool_2].astype(np.float16)

    # 处理帧的函数
    def process_frame(frame_index, frame):
        roi_flat = frame[mask_bool].astype(np.float16)
        diff = np.abs(roi_flat - target_flat)
        diff_mean = np.mean(diff)
        if diff_mean < threshold:
            start_frame = max(0, frame_index - before_frames)
            end_frame = min(total_frames - 1, frame_index + after_frames)
            return range(start_frame, end_frame + 1)

        roi_flat_2 = frame[mask_bool_2].astype(np.float16)
        diff_2 = np.abs(roi_flat_2 - target_flat_2)
        diff_mean_2 = np.mean(diff_2)
        if diff_mean_2 < threshold:
            start_frame = max(0, frame_index - before_frames_2)
            end_frame = min(total_frames - 1, frame_index + after_frames_2)
            return range(start_frame, end_frame + 1)
        return []

    # 使用 deque 存储选中的帧索引
    selected_frames = deque()

    print("正在处理视频帧...")
    with ThreadPoolExecutor(max_workers=num_workers) as executor, tqdm(total=frames_to_process, unit="frame") as pbar:
        futures = []
        frame_index = 0
        while frame_index < frames_to_process:
            if frame_index % 15 == 0:
                ret, frame = cap.read()
                if not ret:
                    break

                futures.append(executor.submit(process_frame, frame_index, frame))
                frame_index += 1
                pbar.update(1)
            else:
                ret = cap.grab()
                if not ret:
                    break

                frame_index += 1
                pbar.update(1)

        # 收集结果
        for future in futures:
            selected_frames.extend(future.result())

    cap.release()

    if not selected_frames:
        print("未找到符合条件的帧")
        return

    # 生成输出视频
    cap = cv2.VideoCapture(input_video)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    print("正在生成新视频...")
    with tqdm(total=frames_to_process, unit="frame") as pbar:
        frame_index = 0
        while frame_index < frames_to_process:
            if frame_index in selected_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            else:
                ret = cap.grab()
                if not ret:
                    break

            frame_index += 1
            pbar.update(1)

    cap.release()
    out.release()
    print(f"处理完成，已生成新视频：{output_video}")

# 示例用法
if __name__ == "__main__":
    # 加载目标图片和遮罩
    target_image = cv2.imread("img.png")
    mask = cv2.imread("mask.png")
    target_image_2 = cv2.imread("img2.png")
    mask_2 = cv2.imread("mask2.png")

    # 调用函数
    # extract_frames_with_condition(
    #     input_video="G:\\2025-02-16_19-19-21.mp4",
    #     output_video="output.mp4",
    #     target_image=target_image,
    #     mask=mask,
    #     target_image_2=target_image_2,
    #     mask_2=mask_2,
    #     threshold=21,
    #     before_seconds=5,
    #     after_seconds=1,
    #     before_seconds_2=1.5,
    #     after_seconds_2=0.001,
    #     max_frames=-1,  # 设置为 -1 表示不限制
    #     num_workers=7  # 使用 7 个线程并行处理
    # )

    # extract_frames_with_condition(
    #     input_video="G:\\2025-02-15_22-16-10.mp4",
    #     output_video="output_2.mp4",
    #     target_image=target_image,
    #     mask=mask,
    #     target_image_2=target_image_2,
    #     mask_2=mask_2,
    #     threshold=21,
    #     before_seconds=5,
    #     after_seconds=1,
    #     before_seconds_2=1.5,
    #     after_seconds_2=0.001,
    #     max_frames=-1,  # 设置为 -1 表示不限制
    #     num_workers=7  # 使用 7 个线程并行处理
    # )

    # extract_frames_with_condition(
    #     input_video="G:\\2025-02-15_18-59-10.mp4",
    #     output_video="output_3.mp4",
    #     target_image=target_image,
    #     mask=mask,
    #     target_image_2=target_image_2,
    #     mask_2=mask_2,
    #     threshold=21,
    #     before_seconds=5,
    #     after_seconds=1,
    #     before_seconds_2=1.5,
    #     after_seconds_2=0.001,
    #     max_frames=-1,  # 设置为 -1 表示不限制
    #     num_workers=7  # 使用 7 个线程并行处理
    # )

    # extract_frames_with_condition(
    #     input_video="G:\\2025-02-15_02-38-25.mp4",
    #     output_video="output_4.mp4",
    #     target_image=target_image,
    #     mask=mask,
    #     target_image_2=target_image_2,
    #     mask_2=mask_2,
    #     threshold=21,
    #     before_seconds=5,
    #     after_seconds=1,
    #     before_seconds_2=1.5,
    #     after_seconds_2=0.001,
    #     max_frames=-1,  # 设置为 -1 表示不限制
    #     num_workers=7  # 使用 7 个线程并行处理
    # )

    extract_frames_with_condition(
        input_video="G:\\2025-02-14_23-27-18.mp4",
        output_video="G:\\output_5.mp4",
        target_image=target_image,
        mask=mask,
        target_image_2=target_image_2,
        mask_2=mask_2,
        threshold=21,
        before_seconds=5,
        after_seconds=1,
        before_seconds_2=1.5,
        after_seconds_2=0.001,
        max_frames=-1,  # 设置为 -1 表示不限制
        num_workers=7  # 使用 7 个线程并行处理
    )
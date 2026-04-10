"""
单帧超分模块
"""
import cv2
import os
from src.core.logger import logger
from src.core.exceptions import MediaProcessError
from .engines import FastUpscaler, FaceFixUpscaler
def run_video_upscale(input_path, output_path, config_manager, method="fast"):
    if not os.path.exists(input_path):
        raise MediaProcessError(f"超分失败：找不到文件 {input_path}")

    scale = config_manager.get("enhancements.scale", 2)
    if method == "face_fix" or method == "pro":
        engine = FaceFixUpscaler(scale=scale)
    else:
        engine = FastUpscaler(scale=scale, sharpness=0.6)
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (w * scale, h * scale)
    )
    logger.info(f"开始渲染增强视频: {total}帧 | 目标分辨率: {w * scale}x{h * scale}")
    try:
        idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            enhanced_frame = engine.process(frame)
            out.write(enhanced_frame)
            idx += 1
            if idx % 50 == 0:
                logger.info(f"进度: {idx}/{total} (引擎: {engine.__class__.__name__})")
    finally:
        cap.release()
        out.release()
    return output_path

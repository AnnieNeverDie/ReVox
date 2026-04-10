import cv2
import numpy as np
import subprocess
import os
import gc
from src.core.logger import logger
def check_ffmpeg_env():
    try:
        result = subprocess.run(["ffmpeg", "-version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True)
        logger.info("FFmpeg 检查通过")
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise EnvironmentError("FFmpeg 未安装或未添加到系统PATH中")

def merge_audio_video(video_path, audio_path, output_path):
    logger.info(f"开始合并音视频: {video_path}, {audio_path}")
    try:
        result = subprocess.run(["ffmpeg", "-encoders"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        encoders_output = result.stdout
        has_libx264 = "libx264" in encoders_output
    except:
        has_libx264 = False
    if has_libx264:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            "-shortest",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "h264",
            "-c:a", "aac",
            "-strict", "experimental",
            "-shortest",
            output_path
        ]
    try:
        result = subprocess.run(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True)
        logger.info(f"音视频合并完成: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.warning("第一次合并失败，尝试备用命令...")
        backup_cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c", "copy",
            "-shortest",
            output_path
        ]
        try:
            result = subprocess.run(backup_cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=True)
            logger.info(f"音视频合并完成（备用）: {output_path}")
            return output_path
        except subprocess.CalledProcessError as backup_error:
            logger.error(f"音视频合并失败: {backup_error.stderr.decode()}")
            raise


def process_video_with_memory_management(input_video_path, process_func, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise IOError(f"无法打开视频文件: {input_video_path}")
    try:
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        processed_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame = process_func(frame)
            out.write(processed_frame)
            del frame
            del processed_frame
            processed_count += 1
            if processed_count % 100 == 0:
                logger.info(f"已处理 {processed_count}/{total_frames} 帧")
                gc.collect()
        logger.info(f"视频处理完成，共处理 {processed_count} 帧")
    finally:
        cap.release()
        if 'out' in locals():
            out.release()
        cv2.destroyAllWindows()
        gc.collect()

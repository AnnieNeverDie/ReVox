"""
信息通用模块
"""
import cv2
import os
from src.core.logger import logger
def get_video_info(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        file_size_bytes = os.path.getsize(video_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        cap.release()
        return {
            'duration': duration,
            'frame_count': frame_count,
            'fps': fps,
            'resolution': f"{width}x{height}",
            'width': width,
            'height': height,
            'file_size_bytes': file_size_bytes,
            'file_size_mb': round(file_size_mb, 2),
            'duration_formatted': f"{int(duration // 60):02d}:{int(duration % 60):02d}"
        }
    except Exception as e:
        logger.error(f"获取视频信息失败: {e}")
        return None


def print_video_info(video_path):
    info = get_video_info(video_path)
    if info:
        logger.info("=" * 50)
        logger.info("生成视频信息:")
        logger.info(f"文件路径: {video_path}")
        logger.info(f"视频时长: {info['duration_formatted']} ({info['duration']:.2f}秒)")
        logger.info(f"分辨率: {info['resolution']}")
        logger.info(f"帧率: {info['fps']:.2f} FPS")
        logger.info(f"总帧数: {info['frame_count']:,}")
        logger.info(f"文件大小: {info['file_size_mb']:.2f} MB")
        logger.info("=" * 50)
    else:
        logger.warning(f"无法获取视频信息: {video_path}")
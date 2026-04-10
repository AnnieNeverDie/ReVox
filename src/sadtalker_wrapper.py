import os
import subprocess
import glob
from src.core.logger import logger
from src.core.exceptions import DependencyError, MediaProcessError
from src.utils.security_utils import (
    safe_path_check,
    validate_file_type,
    SecureFileOperations
)


def run_sadtalker(source_image, driven_audio, config):
    sadtalker_root = config.get("paths.sadtalker_path")
    if not sadtalker_root or not os.path.exists(sadtalker_root):
        raise DependencyError(f"未配置有效的 SadTalker 路径: {sadtalker_root}")
    secure_ops = SecureFileOperations()
    if not safe_path_check(source_image):
        raise ValueError(f"非法的源图像路径: {source_image}")
    if not safe_path_check(driven_audio):
        raise ValueError(f"非法的驱动音频路径: {driven_audio}")
    if not safe_path_check(sadtalker_root):
        raise ValueError(f"非法的SadTalker路径: {sadtalker_root}")
    allowed_image_types = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    allowed_audio_types = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
    if not validate_file_type(source_image, allowed_image_types):
        raise ValueError(f"不支持的图像文件类型: {source_image}")
    if not validate_file_type(driven_audio, allowed_audio_types):
        raise ValueError(f"不支持的音频文件类型: {driven_audio}")
    source_image_abs = os.path.abspath(source_image)
    driven_audio_abs = os.path.abspath(driven_audio)
    result_dir_abs = secure_ops.secure_join(os.getcwd(), "temp_sadtalker")
    secure_ops.secure_mkdir(result_dir_abs)
    sadtalker_root_abs = os.path.abspath(sadtalker_root)
    if not safe_path_check(sadtalker_root_abs):
        raise ValueError(f"非法的SadTalker绝对路径: {sadtalker_root_abs}")
    cmd = [
        "python", os.path.join(sadtalker_root_abs, "inference.py"),
        "--source_image", source_image_abs,
        "--driven_audio", driven_audio_abs,
        "--result_dir", result_dir_abs,
        "--preprocess", config.get("render.preprocess", "full"),
        "--enhancer", "none",
        "--background_enhancer", "none"
    ]
    if config.get("render.still", True):
        cmd.append("--still")
    logger.info(f"启动 SadTalker 底层推理... (目标目录: {result_dir_abs})")
    try:
        result = subprocess.run(
            cmd,
            check=False,
            cwd=sadtalker_root_abs,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            logger.warning(f"SadTalker 进程返回非零代码: {result.returncode}")
            logger.debug(f"SadTalker 错误输出: {result.stderr}")
    except Exception as e:
        logger.error(f"SadTalker 调用发生系统级错误: {e}")
        raise
    search_pattern = os.path.join(result_dir_abs, "**", "*.mp4")
    files = glob.glob(search_pattern, recursive=True)
    if not files:
        raise MediaProcessError("SadTalker 未能生成任何视频产物，请检查显存状态或输入素材。")
    latest_video = max(files, key=os.path.getmtime)
    if not safe_path_check(latest_video):
        raise ValueError(f"非法的视频文件路径: {latest_video}")
    if not validate_file_type(latest_video, ['.mp4', '.avi', '.mov', '.webm']):
        raise ValueError(f"生成的视频文件类型不受支持: {latest_video}")
    logger.info(f"成功捕获 SadTalker 原始视频: {latest_video}")
    return latest_video

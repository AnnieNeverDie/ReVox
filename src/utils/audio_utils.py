"""
音频通用模块
"""
import os
import subprocess
import soundfile as sf
from src.core.logger import logger
from src.core.exceptions import MediaProcessError
def preprocess_audio(input_path, output_path, target_sr=16000):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"音频缺失: {input_path}")
    logger.info(f"音频重采样中: {target_sr}Hz")
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-ar', str(target_sr),
        '-ac', '1',
        output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 重采样失败: {e.stderr.decode()}")
        raise MediaProcessError("音频预处理失败")

def _preprocess_with_ffmpeg(input_path, output_path, target_sr):
    cmd = [
        'ffmpeg', '-i', input_path,
        '-ar', str(target_sr),
        '-ac', '1', '-y', output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise MediaProcessError(f"FFmpeg 音频转换失败: {result.stderr}")
    return output_path

def get_audio_duration(file_path):
    try:
        data, sr = sf.read(file_path)
        return len(data) / sr
    except Exception:
        return 0.0

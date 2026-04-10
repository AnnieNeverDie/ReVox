"""
音频处理模块
"""
import os
import subprocess
import numpy as np
import soundfile as sf
from src.core.logger import logger
from src.core.exceptions import MediaProcessError, ValidationError
def check_audio_quality(path, threshold_db=-60.0):
    if not os.path.exists(path):
        raise ValidationError(f"审计失败：找不到音频文件 {path}")
    try:
        data, sr = sf.read(path)
        if len(data) == 0:
            raise ValidationError("审计失败：音频数据为空")
        rms = np.sqrt(np.mean(data ** 2))
        db = 20 * np.log10(rms) if rms > 0 else -100
        if db < threshold_db:
            logger.warning(f"音频审计警告：检测到音量极低 ({db:.2f}dB)，可能导致数字人嘴部不动。")
            return False
        clipping_count = np.sum(np.abs(data) > 0.99)
        if clipping_count > (len(data) * 0.01):
            logger.warning("音频审计警告：检测到严重爆音，可能影响语音合成质量。")
        logger.info(f"音频审计通过: 采样率 {sr}Hz, 平均音量 {db:.2f}dB")
        return True
    except Exception as e:
        logger.error(f"音频安全性审计过程中发生异常: {e}")
        return False

def process_audio(input_path, output_path):
    if not os.path.exists(input_path):
        raise ValidationError(f"降噪失败：文件不存在 {input_path}")
    is_valid = check_audio_quality(input_path)
    if not is_valid:
        logger.warning("输入音频未通过质量审计，尝试继续降噪，但结果可能不理想。")
    logger.info(f"正在启动 FFmpeg 降噪加速器: {os.path.basename(input_path)}")
    cmd = [
        'ffmpeg', '-i', input_path,
        '-af', 'afftdn=nr=12:nf=-25',
        '-ar', '16000', '-ac', '1', '-y', output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.getsize(output_path) < 1000:
            raise MediaProcessError("降噪输出文件异常（过小），请检查编码器。")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 降噪执行失败，stderr: {e.stderr}")
        raise MediaProcessError(f"音频流处理崩溃: {e.stderr}")
